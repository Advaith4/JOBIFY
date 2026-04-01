Jobify – AI Career Assistant

Jobify is a full-stack AI-powered career assistant that analyzes resumes, suggests relevant job opportunities, improves resume content, and prepares users for interviews using a multi-agent system.

It is designed to demonstrate practical applications of LLMs in real-world workflows, including document parsing, task orchestration, and asynchronous backend systems.

Features
Resume Parsing
Extracts structured text from PDF resumes using pypdf
Works across platforms without external dependencies
Multi-Agent Workflow
Job Finder: Matches user skills with relevant entry-level roles
Resume Optimizer: Improves resume content with ATS-focused suggestions
Interview Coach: Generates tailored technical and behavioral questions
Concurrent Execution
Agents run in parallel using a thread-based architecture
Reduces response time and improves efficiency
API Rate Limit Handling
Implements retry logic with exponential backoff
Handles token limits gracefully without crashing
Web Application
FastAPI backend with async support
Simple and responsive frontend interface
Tech Stack

Backend

Python 3.10+
FastAPI
Uvicorn
CrewAI
LiteLLM

Frontend

HTML5
CSS3
Vanilla JavaScript

AI Models

Groq LLMs (Llama 3 variants)

Parsing & Utilities

pypdf
python-multipart
Getting Started
1. Clone the Repository
git clone https://github.com/yourusername/jobify.git
cd jobify
2. Set Up Virtual Environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Configure Environment Variables

Create a .env file in the root directory:

GROQ_API_KEY=your_api_key_here
5. Run the Application
uvicorn app:app --reload

Open your browser and go to:

http://127.0.0.1:8000

Upload a resume and view the generated results.

Architecture Overview

The system uses a multi-agent design where each agent performs a specific task independently. Execution is handled concurrently using a thread pool.

To manage API rate limits, a retry mechanism with exponential backoff is implemented. This ensures stability and prevents failures when token limits are exceeded.

The backend returns structured responses that are rendered dynamically in the frontend.

Purpose

This project demonstrates:

Practical use of LLM orchestration (CrewAI)
Handling real-world constraints like rate limits
Building scalable backend systems with FastAPI
Integrating AI into user-facing applications
Future Improvements
Multi-turn conversational memory
Job listing API integration
Resume scoring system
Deployment (Docker + cloud)