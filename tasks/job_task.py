from crewai import Task


def create_job_task(agent, resume_content):
    """
    Fully stable version:
    - No f-string issues
    - Clean JSON output
    - Works 100%
    """

    description = """
You are an expert career strategist, recruiter, and job market analyst.

Your job is to deeply analyze the candidate's resume and determine the most suitable
career paths and job opportunities based on their skills, projects, and experience.

---------------------
CANDIDATE RESUME:
{resume}
---------------------

STEP 1: Analyze the resume and identify:
- Core domain (AI, ML, Backend, Web, Data Science, etc.)
- Top 5 strongest skills
- Experience level (Beginner / Intermediate)

STEP 2: Infer the BEST matching job roles dynamically
- Suggest ONLY 2–3 roles based on the user's hard skills.

STEP 3: ACTIVATE YOUR WEB SEARCH TOOL to hunt for LIVE Jobs!
- You MUST use the DuckDuckGoSearch tool to actively search the internet for the roles you inferred (e.g., "entry level Flutter Developer jobs LinkedIn").
- You MUST find EXACTLY 5 REAL, currently open job or internship postings.
- DO NOT hallucinate. Do not skip searching. Only output companies and links that your search tool returned to you in snippets!

FOR EACH JOB, PROVIDE:

1. company:
   - Realistic company name
   - Include startups, mid-size companies, and product companies
   - Avoid ONLY big tech companies (Google, Microsoft, Amazon, etc.)

2. role:
   - Must align with inferred roles

3. required_skills:
   - List of at least 4 relevant technical skills

4. description:
   - 2–3 lines explaining the job role

5. link:
   - MUST be the exact live URL returned from your Web Search Tool snippets.
   - NEVER make up fake links.
   - NEVER invent "https://www.linkedin.com/jobs/search/?keywords=role" templates. Extract real links found on the internet.

IMPORTANT RULES:
- ONLY entry-level or internship roles
- NO senior roles
- NO fake direct job URLs
- DO NOT leave any field empty
- Avoid repeating the same company
- Avoid only top tech companies
- Include startups and mid-size companies

---------------------
OUTPUT FORMAT (STRICT JSON ONLY)
---------------------

RETURN ONLY VALID JSON. NO EXTRA TEXT.

{{
  "suggested_roles": ["role1", "role2", "role3"],
  "jobs": [
    {{
      "company": "string",
      "role": "string",
      "required_skills": ["skill1", "skill2", "skill3", "skill4"],
      "description": "string",
      "link": "string"
    }}
  ]
}}

CRITICAL:
- Output MUST be valid JSON
- Use double quotes only
- No trailing commas
- Must contain EXACTLY 5 jobs
""".format(resume=resume_content)

    task = Task(
        description=description,
        expected_output="""
Valid JSON with:
- suggested_roles
- jobs (5 entries)
""",
        agent=agent
    )

    return task