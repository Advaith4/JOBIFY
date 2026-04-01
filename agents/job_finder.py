from crewai import Agent, LLM
from langchain_community.tools import DuckDuckGoSearchResults
from crewai.tools import tool
import os
from dotenv import load_dotenv

search_instance = DuckDuckGoSearchResults()

@tool("SearchTheInternet")
def search_jobs(query: str) -> str:
    """Useful to search the internet for exact links to active job postings. Returns snippets with links."""
    return search_instance.run(query)

# Load environment variables
load_dotenv()

def create_job_finder():
    """
    Creates and returns the Job Finder Agent
    """

    llm = LLM(
        model="groq/llama-3.1-8b-instant",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )

    job_finder = Agent(
        role="Job Finder",

        goal=(
            "Continuously identify high-quality, relevant job and internship opportunities "
            "tailored to the candidate’s skills, experience, and career goals, while maximizing "
            "their chances of selection by prioritizing roles with strong alignment and growth potential."
        ),

        backstory=(
            "You are a cutting-edge internet-connected technical recruiter. "
            "Instead of generating fake URLs, you use your search tool to surf the web and find ACTIVE job links from real companies."
        ),
        verbose=False,
        allow_delegation=False,
        tools=[search_jobs],
        llm=llm
    )
    
    return job_finder