from crewai import Crew
import concurrent.futures
import json
import re
import time

# ── Agents ─────────────────────────────────────────────────────────────────
from agents.job_finder import create_job_finder
from agents.resume_optimizer import create_resume_optimizer
from agents.interview_coach import create_interview_coach

# ── Tasks ──────────────────────────────────────────────────────────────────
from tasks.job_task import create_role_inference_task, create_job_formatting_task
from tasks.resume_task import create_resume_task
from tasks.interview_task import create_interview_task

# ── Utils ──────────────────────────────────────────────────────────────────
from utils.skill_scorer import compute_match_score, get_priority, generate_action_plan
from utils.job_search import fetch_real_job_snippets


def run_with_retries(func, *args):
    """Exponential backoff for Free Tier APIs (Groq 6000 TPM limit)."""
    for attempt in range(4):
        try:
            return func(*args)
        except Exception as e:
            err = str(e).lower()
            if "rate limit" in err or "429" in err or "decommission" in err:
                delay = 5 * (attempt + 1)
                print(f"⏳ Groq rate limit hit in {func.__name__}. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise e
    return func(*args)


def extract_json(raw):
    """Safely extract JSON from ANY messy LLM output."""
    try:
        return json.loads(raw)
    except Exception:
        pass

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return None


# ── Fallback LinkedIn search URL builder (only used if real search fails) ──
def _linkedin_fallback_url(role: str) -> str:
    encoded = role.replace(" ", "%20")
    return f"https://www.linkedin.com/jobs/search/?keywords={encoded}&f_E=1%2C2"


def run_job_crew(resume_content):
    """
    Two-phase job search pipeline:
      Phase 1 — LLM infers the 5 best matching roles for the candidate.
      Phase 2 — DuckDuckGo fetches REAL search results for those roles.
      Phase 3 — LLM formats the real search data into structured JSON.
    """
    agent = create_job_finder()

    # ── Phase 1: Role Inference ──────────────────────────────────────────────
    print("🔍 Phase 1: Inferring best job roles from resume...")
    infer_task = create_role_inference_task(agent, resume_content)
    infer_crew = Crew(agents=[agent], tasks=[infer_task], verbose=False)
    infer_result = infer_crew.kickoff()
    infer_raw = getattr(infer_result, "raw", str(infer_result)).strip()
    infer_data = extract_json(infer_raw)

    if infer_data and "roles" in infer_data:
        roles = infer_data["roles"]
    else:
        # Fallback roles if parsing fails
        roles = [
            "Junior Software Developer",
            "Backend Developer Intern",
            "Frontend Developer Intern",
            "Data Analyst Intern",
            "Machine Learning Intern",
        ]
    print(f"✅ Inferred roles: {roles}")

    # ── Phase 2: Real Web Search ─────────────────────────────────────────────
    print("🌐 Phase 2: Searching DuckDuckGo for real job postings...")
    search_results = fetch_real_job_snippets(roles)
    print("✅ Real search results fetched.")

    # ── Phase 3: Format Real Results via LLM ────────────────────────────────
    print("🤖 Phase 3: LLM formatting real search results into structured output...")
    format_task = create_job_formatting_task(agent, resume_content, search_results)
    format_crew = Crew(agents=[agent], tasks=[format_task], verbose=False)
    format_result = format_crew.kickoff()
    raw = getattr(format_result, "raw", str(format_result)).strip()
    data = extract_json(raw) or {"suggested_roles": roles, "jobs": []}

    # ── If LLM still produced < 5 jobs, pad with LinkedIn search fallbacks ──
    existing_jobs = data.get("jobs", [])
    while len(existing_jobs) < 5 and roles:
        role = roles[len(existing_jobs)]
        existing_jobs.append({
            "company": "See LinkedIn",
            "role": role,
            "required_skills": [],
            "description": f"Search LinkedIn for '{role}' entry-level positions.",
            "link": _linkedin_fallback_url(role),
        })
    data["jobs"] = existing_jobs[:5]

    # ── Scoring ──────────────────────────────────────────────────────────────
    processed_jobs = []
    for job in data["jobs"]:
        score_data = compute_match_score(resume_content, job.get("required_skills", []))
        job["match_score"] = score_data["score"]
        job["priority"] = get_priority(score_data["score"])
        job["action_plan"] = generate_action_plan(score_data["score"], score_data["missing_keywords"])
        job["matched_skills"] = score_data["matched_keywords"][:5]
        job["missing_skills"] = score_data["missing_keywords"][:5]
        processed_jobs.append(job)

    data["jobs"] = processed_jobs
    return data


def run_resume_crew(resume_content):
    agent = create_resume_optimizer()
    task = create_resume_task(agent, resume_content)
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    raw = getattr(result, "raw", str(result)).strip()
    return extract_json(raw) or {"improvements": []}


def run_interview_crew(resume_content):
    agent = create_interview_coach()
    task = create_interview_task(agent, resume_content)
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    raw = getattr(result, "raw", str(result)).strip()
    return extract_json(raw) or {"questions": []}


def analyze_resume_pipeline(resume_content):
    """
    Runs all 3 agents in parallel and combines the outputs.
    Note: job crew runs multiple phases internally but still kicks off concurrently
    with the other two agents.
    """
    print("🚀 Starting smart parallel analysis pipeline...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_jobs = executor.submit(run_with_retries, run_job_crew, resume_content)

        def run_resume(content):
            time.sleep(2)
            return run_with_retries(run_resume_crew, content)

        def run_interview(content):
            time.sleep(5)
            return run_with_retries(run_interview_crew, content)

        future_resume = executor.submit(run_resume, resume_content)
        future_interview = executor.submit(run_interview, resume_content)

        jobs_data = future_jobs.result()
        resume_data = future_resume.result()
        interview_data = future_interview.result()

    return {
        "roles": jobs_data.get("suggested_roles", []),
        "jobs": jobs_data.get("jobs", []),
        "improvements": resume_data.get("improvements", []),
        "questions": interview_data.get("questions", []),
    }