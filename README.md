# Jobify – AI Career Assistant

Jobify is a full-stack AI-powered career assistant that analyzes resumes, suggests **real** job opportunities from live web search, improves resume content, and prepares users for interviews using a multi-agent system.

---

## Features

### Real-Time Job Search (No Hallucinated Links)
- Uses **DuckDuckGo** (`ddgs`) to fetch live job postings before the LLM runs
- A 3-phase pipeline ensures every job link is a real URL from the web:
  1. **Role Inference** — LLM identifies the 5 best-fit entry-level roles from the resume
  2. **Live Search** — DuckDuckGo fetches real job listings for each inferred role
  3. **Structured Formatting** — LLM formats only the real, pre-fetched data into JSON
- Falls back to a real LinkedIn search URL if DuckDuckGo returns no results

### Resume Parsing
- Extracts structured text from PDF resumes using `pypdf`
- Works across platforms without external dependencies

### Multi-Agent Workflow (CrewAI)
- **Job Finder** — Matches user skills with relevant entry-level roles using real search data
- **Resume Optimizer** — Improves resume content with ATS-focused suggestions
- **Interview Coach** — Generates tailored technical and behavioral questions

### Skill Scorer
- Computes a match score between the candidate's resume and each job's required skills
- Highlights matched and missing skills
- Generates a prioritized action plan for skill gaps

### Concurrent Execution
- All 3 agents run in parallel using a thread-based architecture
- Reduces total response time significantly

### API Rate Limit Handling
- Implements retry logic with exponential backoff for Groq's free tier (6000 TPM)
- Handles token limits gracefully without crashing

### Web Application
- FastAPI backend with async support
- Responsive frontend interface

---

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- Uvicorn
- CrewAI >= 1.0.0

### AI / LLMs
- Groq LLMs (Llama 3.1 8B Instant)

### Job Search
- `ddgs` (DuckDuckGo Search — no API key required)

### Parsing & Utilities
- `pypdf`
- `python-multipart`
- `python-dotenv`

### Frontend
- HTML5, CSS3, Vanilla JavaScript

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Advaith4/JOBIFY.git
cd JOBIFY
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at: https://console.groq.com

> **Note:** No other API keys are required. Job search uses DuckDuckGo which is free and requires no key.

### 5. Run the Application
```bash
uvicorn app:app --reload
```

Open your browser and go to: **http://127.0.0.1:8000**

Upload a resume (PDF) and view the generated results.

---

## Architecture Overview

```
Resume PDF
    │
    ▼
PDF Parser (pypdf)
    │
    ├─────────────────────────────────────────────────────┐
    │                                                     │
    ▼                                                     ▼
Job Finder Pipeline                          Resume Optimizer + Interview Coach
  Phase 1: LLM infers 5 best roles            (run concurrently via ThreadPoolExecutor)
  Phase 2: DuckDuckGo fetches real URLs
  Phase 3: LLM formats real data → JSON
    │
    ▼
Skill Scorer
  - Match score vs required skills
  - Identifies gaps + action plan
    │
    ▼
FastAPI → JSON Response → Frontend
```

Rate limits are handled with exponential backoff so the app never crashes on Groq's free tier.

---

## Purpose

This project demonstrates:

- Practical use of LLM orchestration (CrewAI)
- Real-time web search integration without a dedicated job API
- Eliminating LLM hallucinations via a search-first pipeline design
- Handling real-world constraints like API rate limits
- Building scalable backend systems with FastAPI
- Integrating AI into user-facing applications

---

## Future Improvements

- Multi-turn conversational memory
- ATS resume scoring with detailed feedback
- Deployment (Docker + cloud)
- User accounts and saved results