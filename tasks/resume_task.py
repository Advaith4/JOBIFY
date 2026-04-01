from crewai import Task

def create_resume_task(agent, resume_content):
    description = """
You are a Resume Optimizer.
Analyze the following resume:

---------------------
{resume}
---------------------

Provide EXACTLY 4 actionable improvement points to make this resume better.
Focus on:
1. Action verbs and quantifying metrics.
2. Formatting or structural gaps.
3. Highlighting key skills better.

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "improvements": [
    "improvement 1",
    "improvement 2",
    "improvement 3",
    "improvement 4"
  ]
}}
""".format(resume=resume_content)

    return Task(
        description=description,
        expected_output="Valid JSON containing exactly 4 resume improvements.",
        agent=agent
    )
