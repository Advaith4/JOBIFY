from crewai import Crew
from agents.job_finder import create_job_finder
from tasks.job_task import create_job_task

import json
import re

from utils.skill_scorer import (
    compute_match_score,
    get_priority,
    generate_action_plan
)


def load_resume(file_path="data/resume.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading resume: {e}")
        return ""


def extract_json(raw):
    """
    Safely extract JSON from ANY messy LLM output
    """
    try:
        # Case 1: already clean JSON
        return json.loads(raw)
    except:
        pass

    try:
        # Case 2: extract JSON block using regex
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass

    return None


def run_war_room():
    print("\n🚀 Running Jobify...\n")

    resume_content = load_resume()

    if not resume_content:
        print("❌ Resume is empty. Exiting...")
        return

    job_finder = create_job_finder()
    job_task = create_job_task(job_finder, resume_content)

    crew = Crew(
        agents=[job_finder],
        tasks=[job_task],
        verbose=True
    )

    result = crew.kickoff()

    # 🔥 HANDLE ALL POSSIBLE OUTPUT TYPES
    raw_output = None

    if hasattr(result, "raw"):
        raw_output = result.raw
    else:
        raw_output = str(result)

    raw_output = raw_output.strip()

    data = extract_json(raw_output)

    if not data:
        print("❌ JSON parsing failed completely")
        print("\nRaw Output:\n", raw_output)
        return

    # 🎯 DISPLAY
    print("\n🎯 Suggested Roles:\n")
    for role in data.get("suggested_roles", []):
        print(f"- {role}")

    print("\n📌 Job Opportunities:\n")

    for i, job in enumerate(data.get("jobs", []), start=1):
        print("=" * 60)
        print(f"🔹 Job {i}")
        print(f"🏢 Company: {job.get('company')}")
        print(f"💼 Role: {job.get('role')}")

        job_text = " ".join(job.get("required_skills", [])) + " " + job.get("description", "")

        score_data = compute_match_score(resume_content, job_text)

        score = score_data["score"]
        priority = get_priority(score)
        action_plan = generate_action_plan(score, score_data["missing_keywords"])

        print(f"\n📊 Match Score: {score}%")
        print(f"🎯 Priority: {priority}")

        print("\n✅ Matched Skills:")
        print(", ".join(score_data["matched_keywords"][:5]) or "None")

        print("\n❌ Missing Skills:")
        print(", ".join(score_data["missing_keywords"][:5]) or "None")

        print(f"\n🧠 Action Plan: {action_plan}")

        print(f"\n🔗 Apply Here: {job.get('link')}")
        print("=" * 60)

    print("\n🔥 DONE. No crashes. No nonsense.\n")


if __name__ == "__main__":
    run_war_room()