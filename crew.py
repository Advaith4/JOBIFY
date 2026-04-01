from crewai import Crew
from agents.job_finder import create_job_finder
from tasks.job_task import create_job_task

# 🔹 Load resume content
def load_resume():
    with open("data/resume.txt", "r", encoding="utf-8") as f:
        return f.read()


def run_war_room(role="Software Engineer Intern"):
    
    # Load resume
    resume_content = load_resume()

    # Create agent
    job_finder = create_job_finder()

    # Create task (NOW with resume)
    job_task = create_job_task(job_finder, role, resume_content)

    # Create crew
    crew = Crew(
        agents=[job_finder],
        tasks=[job_task],
        verbose=True
    )

    # Run system
    result = crew.kickoff()

    return result


if __name__ == "__main__":
    output = run_war_room()
    print("\n🔥 FINAL OUTPUT:\n")
    print(output)