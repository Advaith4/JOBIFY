from crewai import Agent, LLM
import os
from dotenv import load_dotenv

load_dotenv()

def create_interview_coach():
    llm = LLM(
        model="groq/llama-3.1-8b-instant",
        temperature=0.4,
        api_key=os.getenv("GROQ_API_KEY")
    )

    return Agent(
        role="Interview Coach",
        goal="Generate challenging but realistic technical and behavioral interview questions tailored to the candidate's core skills.",
        backstory=(
            "You are an elite technical interviewer at a top-tier tech company. "
            "You test candidates not just on syntax, but on problem-solving, system design, and behavioral adaptability based on their past experiences."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
