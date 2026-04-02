from crewai import Task


def create_role_inference_task(agent, resume_content):
    """
    Phase 1: Just infer the 5 best matching job roles for this candidate.
    Returns a simple JSON list — fast and cheap on tokens.
    """
    description = (
        "Analyze the following resume and identify the 5 best entry-level or internship "
        "job roles for this candidate based on their skills, projects, and experience.\n\n"
        "CANDIDATE RESUME:\n"
        "---------------------\n"
        f"{resume_content}\n"
        "---------------------\n\n"
        "Return ONLY a valid JSON object in EXACTLY this format (no extra text):\n"
        '{{"roles": ["Role 1", "Role 2", "Role 3", "Role 4", "Role 5"]}}\n\n'
        "Rules:\n"
        "- Only entry-level, junior, or internship roles\n"
        "- Be specific (e.g. 'Junior Flutter Developer', not just 'Developer')\n"
        "- 5 distinct, different roles\n"
        "- No senior or lead positions\n"
        "- Output must be valid JSON, no markdown, no explanation"
    )

    return Task(
        description=description,
        expected_output='JSON: {"roles": ["role1", "role2", "role3", "role4", "role5"]}',
        agent=agent
    )


def create_job_formatting_task(agent, resume_content, search_results: str):
    """
    Phase 2: Given REAL search results from DuckDuckGo, extract and format
    structured job listings. The LLM's only job is to parse and format
    real data — not to invent anything.
    """
    description = (
        "You are a career strategist. Below you will find REAL job search results "
        "fetched from DuckDuckGo. Your job is to read these results carefully and "
        "extract 5 real job opportunities for the candidate.\n\n"

        "CANDIDATE RESUME SUMMARY:\n"
        "---------------------\n"
        f"{resume_content[:1500]}\n"  # trim for token efficiency
        "---------------------\n\n"

        "REAL JOB SEARCH RESULTS (from live DuckDuckGo search):\n"
        "---------------------\n"
        f"{search_results}\n"
        "---------------------\n\n"

        "INSTRUCTIONS:\n"
        "1. From the search results above, pick the 5 most relevant job postings.\n"
        "2. For each job use ONLY data from the search results — DO NOT invent a company name, "
        "   role title, or URL.\n"
        "3. The 'link' field MUST be the exact URL shown in the search results.\n"
        "4. If a search result has no clear company, use the domain of the URL as the company "
        "   name (e.g. 'indeed.com' → 'Indeed Listing').\n"
        "5. required_skills: list 4 relevant skills based on the job snippet and the candidate's resume.\n"
        "6. description: 2–3 sentences describing the role from the snippet.\n\n"

        "OUTPUT FORMAT (STRICT JSON ONLY):\n"
        "{{\n"
        '  "suggested_roles": ["role1", "role2", "role3", "role4", "role5"],\n'
        '  "jobs": [\n'
        "    {{\n"
        '      "company": "string",\n'
        '      "role": "string",\n'
        '      "required_skills": ["skill1", "skill2", "skill3", "skill4"],\n'
        '      "description": "string",\n'
        '      "link": "string"\n'
        "    }}\n"
        "  ]\n"
        "}}\n\n"
        "CRITICAL:\n"
        "- Output MUST be valid JSON, no extra text\n"
        "- Use double quotes only\n"
        "- No trailing commas\n"
        "- Must contain EXACTLY 5 jobs\n"
        "- Every 'link' must be one of the exact URLs from the search results above\n"
    )

    return Task(
        description=description,
        expected_output=(
            "Valid JSON with suggested_roles and 5 jobs, each with a real URL from search results."
        ),
        agent=agent
    )