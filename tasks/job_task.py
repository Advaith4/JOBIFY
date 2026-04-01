from crewai import Task

def create_job_task(agent, role, resume_content):
    """
    Creates a high-quality job finding task tailored to the user's profile
    """

    task = Task(
        description=f"""
        You are an expert job researcher.

        Your task is to find 5 HIGHLY RELEVANT and RECENT job or internship opportunities 
        for the role: {role}.

        The candidate is a 3rd-year college student with the following profile:
        ---------------------
        {resume_content}
        ---------------------

        STRICT INSTRUCTIONS:
        - Focus on entry-level / internship roles only
        - Ensure jobs are realistic and currently available
        - Prefer companies that hire students or freshers
        - Avoid irrelevant senior-level roles

        FOR EACH JOB, PROVIDE:
        1. Company Name
        2. Role Title
        3. Required Skills (bullet points)
        4. Why this job matches the candidate (IMPORTANT)
        5. Key skills the candidate is missing (IMPORTANT)
        6. Short job description (2-3 lines)
        7. Application link (if possible)

        OUTPUT FORMAT:
        - Clean, structured, easy to read
        - No unnecessary text
        - Use clear headings for each job

        Your goal is to help the candidate ACTUALLY APPLY and GET SELECTED.
        """,

        expected_output="""
        A structured list of 5 personalized job opportunities with match analysis,
        missing skills, and application details.
        """,

        agent=agent
    )

    return task