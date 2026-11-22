from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO
from datetime import datetime
import requests

from docx import Document
from docx.shared import Pt

app = FastAPI(title="AI Accomplishment Report Generator")

# Allow our React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma3:1b"


class ReportRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {"message": "Accomplishment Report Generator is running"}


@app.get("/api/health")
def health_check():
    return {"status": "online", "model": OLLAMA_MODEL}


@app.post("/api/generate-docx")
def generate_docx(request: ReportRequest):

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter your accomplishment details."
        )

    # 1. Ask Ollama to improve the raw text
    prompt = f"""
You are an assistant that rewrites faculty accomplishment notes
into professional entries for a university accomplishment report.

Your task is to improve the grammar, clarity, and professionalism
of the input while preserving the original meaning.

STRICT RULES:

1. ALWAYS use past tense because the accomplishments describe
   activities that have already been completed.

2. Do not use phrases such as:
   - "The faculty member..."
   - "The instructor..."
   - "The professor..."
   - "is currently discussing..."
   - "is conducting..."
   - "was responsible for..."

3. Start directly with the action performed.
   Examples:
   - Discussed...
   - Conducted...
   - Introduced...
   - Facilitated...
   - Explained...
   - Presented...
   - Continued...

4. NEVER change the names of subjects or courses provided
   in the input.

   For example:
   "Introduction to Computing" must remain "Introduction to Computing".
   Do not rename it to "Computer Science", "Introductory Computer
   Science", or any other similar course title.

5. Do not assume, add, or invent activities, outcomes, details,
   or accomplishments that are not mentioned in the input.

6. Keep the output concise, natural, and appropriate for an
   official faculty accomplishment report.

7. Translate mixed-language input into professional English,
   but preserve technical terms and official subject names.

8. Do not add explanations, introductory statements, headings,
   quotation marks, or commentary.

9. Return ONLY the final accomplishment statement.

EXAMPLE:

Input:
nag continue sa pag discuss sa next topic which is ang linked list
for data structure and algorithm nga subject, and introduce the
number system and data representaion for introduction to computer
subject.

Output:
Continued the discussion on Linked Lists in Data Structures and
Algorithms (DSA), and introduced Number Systems and Data
Representation in Introduction to Computing, following the syllabus.

NOW REWRITE THIS INPUT:

{request.text}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=180
        )

        response.raise_for_status()

        ai_text = response.json()["message"]["content"].strip()

    except requests.Timeout:
        raise HTTPException(
            status_code=504,
            detail="The AI model took too long to respond."
        )

    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to Ollama. Make sure Ollama is running."
        )

    # 2. Create the Word document
    document = Document()

    # Document title
    title = document.add_heading(
        "ACCOMPLISHMENT REPORT",
        level=1
    )
    title.alignment = 1  # Center

    # Generated date
    date_text = datetime.now().strftime("%B %d, %Y")

    document.add_paragraph(f"Date Generated: {date_text}")

    document.add_heading("Accomplishment", level=2)

    document.add_paragraph(ai_text)

    # Basic formatting
    for paragraph in document.paragraphs:
        for run in paragraph.runs:
            run.font.name = "Arial"
            run.font.size = Pt(11)

    # 3. Save the document into memory instead of disk
    file_buffer = BytesIO()
    document.save(file_buffer)
    file_buffer.seek(0)

    # 4. Send the DOCX file to React
    return StreamingResponse(
        file_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": 'attachment; filename="Accomplishment_Report.docx"'
        }
    )