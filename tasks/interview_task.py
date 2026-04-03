from crewai import Task

# Legacy implementation for /api/analyze UI
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
      "type": "Behavioral",
      "question": "string",
      "tip": "string"
    }}
  ]
}}
""".format(resume=resume_content)
    return Task(
        description=description,
        expected_output="Valid JSON containing exactly 4 interview questions with tips.",
        agent=agent
    )

def create_interview_start_task(agent, role, difficulty):
    description = """
You are the Interviewer.
The candidate is applying for the role: {role}.
The current difficulty level is {difficulty}/10.

Generate exactly ONE targeted interview question for this candidate.
If the difficulty is high (7-10), make it a system design or deep architectural question.
If the difficulty is medium (4-6), make it a practical coding or scenario question.
If the difficulty is low (1-3), make it a basic conceptual or behavioral question.

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "question": "The interview question string"
}}
""".format(role=role, difficulty=difficulty)

    return Task(
        description=description,
        expected_output="Valid JSON with a single interview question.",
        agent=agent
    )

def create_evaluator_task(agent, question, answer):
    description = """
You are the Evaluator.
Review the candidate's answer to the following question:

Question: {question}
Candidate Answer: {answer}

Provide a strict score from 1 to 10. 
CRITICAL RULES FOR SCORING:
- If the question asked for code or steps and the answer is just one sentence, MAXIMUM score is 4.
- If the candidate says "I don't know", the score MUST be 1 or 2.
- Only award 8-10 for comprehensive, technically accurate, and well-structured answers.

List strengths (if any), weaknesses, and a concrete suggestion for improvement.

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "score": 8,
  "strengths": ["...", "..."],
  "weaknesses": ["..."],
  "improvements": "..."
}}
""".format(question=question, answer=answer)

    return Task(
        description=description,
        expected_output="Valid JSON with score, strengths, weaknesses, and improvements.",
        agent=agent
    )

def create_followup_task(agent, role, question, answer, difficulty):
    description = """
You are the Follow-up Interviewer.
Role: {role}.
Difficulty: {difficulty}/10.

Question Asked: {question}
Candidate Answer: {answer}

Based on the answer, generate exactly ONE follow-up question. 
- If the candidate gave a strong answer, dig deeper into a missing detail, ask them to optimize their approach, or introduce a constraint.
- If the candidate struggled or said "I don't know", step back and ask a much more fundamental, basic conceptual question related to the topic (e.g. "Let's step back, can you explain what a Recommendation System does in general?").

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "question": "The follow-up interview question string"
}}
""".format(role=role, question=question, answer=answer, difficulty=difficulty)

    return Task(
        description=description,
        expected_output="Valid JSON with a single follow-up question.",
        agent=agent
    )

def create_difficulty_task(agent, current_difficulty, score):
    description = """
You are the Difficulty Controller.
Current Difficulty: {current_difficulty}/10
Last Answer Score: {score}/10

Adjust the difficulty for the next question.
Rule of thumb:
- If score >= 8: increase difficulty by 1.
- If score <= 4: decrease difficulty by 1.
- Else: keep it the same.
Difficulty must stay between 1 and 10.

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "new_difficulty": 5
}}
""".format(current_difficulty=current_difficulty, score=score)

    return Task(
        description=description,
        expected_output="Valid JSON with the new integer difficulty.",
        agent=agent
    )
