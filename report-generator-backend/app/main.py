from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO
from datetime import datetime
import requests
import sqlite3
from pathlib import Path
from uuid import uuid4
import re

from fastapi import UploadFile, File
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
OLLAMA_MODEL = "qwen3.5:4b"

# Knowledge Base storage
BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "knowledge_base"
UPLOAD_DIR = KB_DIR / "uploads"
DB_PATH = KB_DIR / "knowledge.db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_knowledge_base():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


initialize_knowledge_base()

from docx import Document
from io import BytesIO


def extract_docx_text(file_bytes: bytes) -> str:
    document = Document(BytesIO(file_bytes))
    extracted_parts = []

    # Extract normal paragraphs
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            extracted_parts.append(text)

    # Extract table contents (important for accomplishment reports)
    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            )

            if row_text:
                extracted_parts.append(row_text)

    return "\n".join(extracted_parts)

class ReportRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {"message": "Accomplishment Report Generator is running"}


@app.get("/api/health")
def health_check():
    return {"status": "online", "model": OLLAMA_MODEL}

def retrieve_relevant_examples(query: str, limit: int = 5):
    """
    Retrieve historical accomplishment entries using keyword overlap.
    """

    stopwords = {
        "the", "and", "for", "was", "were", "are", "is",
        "this", "that", "with", "from", "into", "about",
        "their", "them", "they", "then", "have", "has",
        "had", "been", "being", "his", "her", "its",
        "a", "an", "to", "of", "in", "on", "at", "by",
        "as", "or", "but", "not", "we", "it", "he", "she",
        "while", "during", "through", "after", "before"
    }

    def tokenize(text):
        words = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return {
            word for word in words
            if len(word) > 2 and word not in stopwords
        }

    query_words = tokenize(query)

    if not query_words:
        return []

    # Retrieve all stored reports
    with get_db() as conn:
        reports = conn.execute(
            "SELECT filename, extracted_text FROM reports"
        ).fetchall()

    candidates = []

    # Split reports into smaller entries instead of searching entire documents
    for report in reports:
        lines = report["extracted_text"].splitlines()

        for line in lines:
            line = line.strip()

            if len(line) < 15:
                continue

            entry_words = tokenize(line)

            if not entry_words:
                continue

            # Count shared keywords
            matched_words = query_words.intersection(entry_words)
            score = len(matched_words)

            if score > 0:
                candidates.append({
                    "text": line,
                    "source": report["filename"],
                    "score": score
                })

    # Highest similarity score first
    candidates.sort(key=lambda item: item["score"], reverse=True)

    # Remove duplicate text
    results = []
    seen = set()

    for candidate in candidates:
        text = candidate["text"]

        if text in seen:
            continue

        seen.add(text)
        results.append(candidate)

        if len(results) >= limit:
            break

    return results

@app.post("/api/generate-docx")
def generate_docx(request: ReportRequest):

    # 1. Search our Knowledge Base for similar accomplishments
    examples = retrieve_relevant_examples(request.text)

    # 2. Convert retrieved examples into context text
    if examples:
        reference_text = "\n".join(
            f"- {item['text']}"
            for item in examples
        )
    else:
        reference_text = "No relevant historical examples were found."

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter your accomplishment details."
        )

    # 1. Ask Ollama to improve the raw text
    prompt = f"""
You are an assistant that writes professional faculty accomplishment reports
for Southern Leyte State University.

Your job is to rewrite the faculty's raw notes into concise,
professional accomplishment statements.

HISTORICAL ACCOMPLISHMENT REFERENCES:
{reference_text}

IMPORTANT RULES:

1. Use the historical references ONLY as examples of writing style,
   terminology, and phrasing.

2. Do not copy historical activities as if they were performed
   during the current reporting period.

3. Only describe activities explicitly mentioned in the CURRENT INPUT.

4. Always use past tense.

5. Start directly with the activity.
   Examples: Discussed, Continued, Introduced, Conducted,
   Facilitated, Explained, Presented, Prepared, Uploaded.

6. Never start with:
   "The faculty member..."
   "The instructor..."
   "The professor..."
   "Currently..."

7. Preserve the official subject names provided in the input.
   For example, "Introduction to Computing" must not be renamed
   to "Computer Science."

8. Translate Bisaya, Taglish, or informal wording into professional
   English while preserving the original meaning.

9. Do not invent activities, student outcomes, or details.

10. Return ONLY the accomplishment statement.
    Do not include explanations, headings, or quotation marks.

STYLE EXAMPLE:

Input:
nag continue sa pag discuss sa next topic which is ang linked list
for data structure and algorithm nga subject, and introduce the
number system and data representaion for introduction to computer subject.

Output:
Continued the discussion on Linked Lists in Data Structures and
Algorithms (DSA), and introduced Number Systems and Data
Representation in Introduction to Computing.

CURRENT INPUT:
{request.text}

FINAL ACCOMPLISHMENT:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "think": False,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 150
                }
            },
            timeout=300
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

@app.post("/api/knowledge/upload")
async def upload_report(file: UploadFile = File(...)):

    # Only allow DOCX for now
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail="Only DOCX files are supported."
        )

    file_bytes = await file.read()

    # Limit upload size to 10 MB
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File exceeds the 10 MB limit."
        )

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    try:
        extracted_text = extract_docx_text(file_bytes)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text was found in the document."
            )

        # Create unique filename to prevent collisions
        stored_filename = f"{uuid4().hex}.docx"
        file_path = UPLOAD_DIR / stored_filename

        # Save the original DOCX
        file_path.write_bytes(file_bytes)

        # Save extracted text into SQLite
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO reports
                (filename, stored_filename, extracted_text)
                VALUES (?, ?, ?)
                """,
                (
                    file.filename,
                    stored_filename,
                    extracted_text
                )
            )

            report_id = cursor.lastrowid

        return {
            "message": "Report uploaded successfully.",
            "id": report_id,
            "filename": file.filename,
            "extracted_text": extracted_text
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )
    
@app.get("/api/knowledge")
def get_knowledge_reports():

    with get_db() as conn:
        reports = conn.execute(
            """
            SELECT id, filename, uploaded_at, extracted_text
            FROM reports
            ORDER BY uploaded_at DESC
            """
        ).fetchall()

    return [
        {
            "id": report["id"],
            "filename": report["filename"],
            "uploaded_at": report["uploaded_at"],
            "text_preview": report["extracted_text"][:300]
        }
        for report in reports
    ]

@app.get("/api/knowledge/{report_id}")
def get_knowledge_report(report_id: int):

    with get_db() as conn:
        report = conn.execute(
            """
            SELECT *
            FROM reports
            WHERE id = ?
            """,
            (report_id,)
        ).fetchone()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found."
        )

    return {
        "id": report["id"],
        "filename": report["filename"],
        "uploaded_at": report["uploaded_at"],
        "extracted_text": report["extracted_text"]
    }

@app.delete("/api/knowledge/{report_id}")
def delete_knowledge_report(report_id: int):

    with get_db() as conn:
        report = conn.execute(
            """
            SELECT stored_filename
            FROM reports
            WHERE id = ?
            """,
            (report_id,)
        ).fetchone()

        if not report:
            raise HTTPException(
                status_code=404,
                detail="Report not found."
            )

        # Delete the uploaded file
        file_path = UPLOAD_DIR / report["stored_filename"]

        if file_path.exists():
            file_path.unlink()

        # Delete the database record
        conn.execute(
            "DELETE FROM reports WHERE id = ?",
            (report_id,)
        )

    return {
        "message": "Report deleted successfully."
    }