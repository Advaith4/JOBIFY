from crewai import Agent, LLM
import os
from dotenv import load_dotenv

load_dotenv()

def create_resume_optimizer():
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        temperature=0.4,
        api_key=os.getenv("GROQ_API_KEY")
    )

    return Agent(
        role="Resume Optimizer",
        goal="Analyze the candidate's resume and provide precise, actionable improvements to make it stand out to ATS systems and human recruiters.",
        backstory=(
            "You are a seasoned technical recruiter and expert resume writer. "
            "You know exactly what hiring managers look for—impact, metrics, and clarity. "
            "You find formatting gaps, weak verbs, and poor skills presentation, and give exact advice to fix them."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
