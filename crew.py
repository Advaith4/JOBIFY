from crewai import Crew
import concurrent.futures
import json
import re
import time

def run_with_retries(func, *args):
    """Graceful exponential backoff for Free Tier APIs (Groq 6000 TPM limit)"""
    for attempt in range(4):
        try:
            return func(*args)
        except Exception as e:
            err = str(e).lower()
            if "rate limit" in err or "429" in err or "decommission" in err:
                delay = 5 * (attempt + 1)
                print(f"⏳ Groq rate limit exceeded in {func.__name__}. Sleeping {delay} seconds...")
                time.sleep(delay)
            else:
                raise e
    return func(*args)

# Import agents
from agents.job_finder import create_job_finder
from agents.resume_optimizer import create_resume_optimizer
from agents.interview_coach import create_interview_coach

# Import tasks
from tasks.job_task import create_job_task
from tasks.resume_task import create_resume_task
from tasks.interview_task import create_interview_task

# Import utils
from utils.skill_scorer import compute_match_score, get_priority, generate_action_plan

def extract_json(raw):
    """
    Safely extract JSON from ANY messy LLM output
    """
    try:
        return json.loads(raw)
    except:
        pass

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass

    return None

def run_job_crew(resume_content):
    agent = create_job_finder()
    task = create_job_task(agent, resume_content)
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    raw = getattr(result, "raw", str(result)).strip()
    data = extract_json(raw) or {"suggested_roles": [], "jobs": []}
    
    # Run the scorer on the raw jobs
    processed_jobs = []
    for job in data.get("jobs", []):
        job_text = " ".join(job.get("required_skills", [])) + " " + job.get("description", "")
        score_data = compute_match_score(resume_content, job_text)
        
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
    """
    print("Starting smart parallel analysis pipeline...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_jobs = executor.submit(run_with_retries, run_job_crew, resume_content)
        
        # Stagger the next requests by a few seconds to let Groq's token bucket refill smoothly
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
        "questions": interview_data.get("questions", [])
    }