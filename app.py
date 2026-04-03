from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
import logging

from utils.resume_parser import extract_text_from_pdf
from crew import analyze_resume_pipeline

logger = logging.getLogger(__name__)

app = FastAPI(title="Jobify API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes will be evaluated in order

@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    location: str = Form(default="India"),
    job_type: str = Form(default="Full-time"),
    work_mode: str = Form(default="Any"),
    experience: str = Form(default="Entry-level")
):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Only PDF files are supported."})

    # Use UUID to avoid filename collisions in concurrent uploads
    if not os.path.exists("data"):
        os.makedirs("data")

    temp_path = f"data/resume_{uuid.uuid4().hex}.pdf"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 1. Extract text from PDF
        resume_content = extract_text_from_pdf(temp_path)
        
        if not resume_content or len(resume_content) < 50:
            return JSONResponse(status_code=400, content={"error": "Could not extract sufficient text from the PDF. Make sure it is text-based."})
            
        # 2. Run the AI Pipeline
        prefs = {
            "location": location,
            "job_type": job_type,
            "work_mode": work_mode,
            "experience": experience
        }
        results = analyze_resume_pipeline(resume_content, prefs)
        
        return JSONResponse(content=results)
        
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print("API ERROR CAUGHT:", err_msg)
        return JSONResponse(status_code=500, content={"error": f"{str(e)} | Details: {err_msg}"})
    finally:
        # Clean up the temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

# Mount the static directory for the Frontend (MUST BE LAST)
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Make sure to run with: uvicorn app:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
