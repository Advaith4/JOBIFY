# Jobify.ai – AI Career Assistant

Jobify is a full-stack AI-powered career assistant that analyzes resumes, maps out user preferences, suggests **real** job opportunities via live API searches, improves resume content with ATS feedback, and generates tailored interview prep using a parallel multi-agent system.

---

## Features

### Real-Time Live Job Search
- Uses **JSearch API (RapidAPI)** to fetch live, structured job postings before the LLM runs.
- A 3-phase **Hybrid RAG** pipeline ensures zero hallucinations:
  1. **Role Inference** — LLM identifies the 5 best-fit entry/junior level roles based on the candidate's core skills and their inputted Location/Experience preferences.
  2. **Live Retrieval** — Fetches real job listings for those roles across varied query combinations.
  3. **Ranking** — LLM formats, scores, and ranks only the *real*, pre-fetched jobs.

### Dynamic User Preferences
- In-UI form to seamlessly ask candidates for their preferred **Location, Job Type (Full-time/Intern), Work Mode (Remote/Hybrid), and Experience Level**.
- Dynamically integrates context directly into search queries.

### Resume Parsing
- Extracts structured text from PDF resumes using `pypdf`.
- Implements **safe, UUID-based temporal file storage** to support simultaneous user concurrency.

### Multi-Agent Workflow (CrewAI)
- **Job Finder** — RAG architecture to match candidate skills with verified live API links.
- **Resume Optimizer** — Improves weaknesses and provides actionable ATS-focused suggestions.
- **Interview Coach** — Generates customized technical and behavioral mock questions.

### Performance & Stability
- Agents execute **concurrently** via a threaded engine to reduce wait times by over 20 seconds.
- Handled via `FastAPI` with asynchronous endpoints.
- Auto-retries with exponential backoff on LLM rate limits (`Groq` 6000 TPM limit handling).

---

## Tech Stack

### Backend
- Python 3.10+
- FastAPI, Uvicorn
- CrewAI (Multi-Agent System)
- Groq LLMs (Llama 3.3 70B Versatile)

### Job Search API
- **JSearch API** via RapidAPI (Retrieves live LinkedIn/Google jobs data natively)

### Frontend
- HTML5, Vanilla CSS3, Vanilla JavaScript (Zero bloated frameworks)

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
Create a `.env` file in the root directory (see `.env.example`):
```
GROQ_API_KEY=your_groq_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
```
1. **Groq**: Get a free API key at: [console.groq.com](https://console.groq.com)
2. **RapidAPI (JSearch)**: Subscribe for free at [rapidapi.com](https://rapidapi.com/letscrape-6bRBa3QGz9/api/jsearch)

### 5. Run the Application
```bash
uvicorn app:app --reload
```
Open your browser and navigate to: **http://127.0.0.1:8000**

---

## Architecture Overview

```
Resume PDF + User Preferences
    │
    ▼
File Handler (UUID Concurrency)
    │
    ▼
PDF Parser (pypdf)
    │
    ├────────────────────────────────────────────────────────┐
    │                                                        │
    ▼                                                        ▼
Job Finder Pipeline (Hybrid RAG)                 Resume Optimizer + Interview Coach
  Phase 1: LLM infers roles + preferences          (run concurrently via ThreadPoolExecutor)
  Phase 2: JSearch API fetches live data
  Phase 3: LLM ranks & scores real data
    │
    ▼
FastAPI JSON Response
    │
    ▼
Vanilla JS Frontend (Dynamic DOM Render)
```

---

## Purpose

This project demonstrates:
- Practical use of **LLM orchestration (CrewAI)** combined with external APIs.
- Eradicating LLM hallucination in generation tasks via a **strict RAG design**.
- Managing high-latency parallel operations with Python thread pooling.
- Delivering a massive amount of functionality using simple but elegant API-to-UI binding.