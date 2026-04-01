from crewai import Task

def create_interview_task(agent, resume_content):
    description = """
You are an Interview Coach.
Analyze the following resume:

---------------------
{resume}
---------------------

Based on the candidate's experience and skills, generate EXACTLY 4 interview questions they are likely to face.
Include 2 technical questions (based on their tools/languages) and 2 behavioral questions. Provide a short tip on how to answer each.

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "questions": [
    {{
      "type": "Technical",
      "question": "string",
      "tip": "string"
    }},
    {{
      "type": "Technical",
      "question": "string",
      "tip": "string"
    }},
    {{
      "type": "Behavioral",
      "question": "string",
      "tip": "string"
    }},
    {{
      "type": "Behavioral",
      "question": "string",
      "tip": "string"
    }}
  ]
}}

CRITICAL:
- ONLY output JSON
- Do not add markdown backticks if not necessary, just ensure it parses as JSON.
""".format(resume=resume_content)

    return Task(
        description=description,
        expected_output="Valid JSON containing exactly 4 interview questions with tips.",
        agent=agent
    )
