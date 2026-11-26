from contextlib import closing
from typing import Optional

from app.database.connection import get_db, UPLOAD_DIR


def insert_report(filename: str, stored_filename: str, extracted_text: str) -> int:
    """Save a report record and return its new ID."""
    with closing(get_db()) as conn:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO reports (filename, stored_filename, extracted_text)
                VALUES (?, ?, ?)
                """,
                (filename, stored_filename, extracted_text),
            )
            return cursor.lastrowid


def list_reports() -> list[dict]:
    """Return all reports, newest first, with a short text preview."""
    with closing(get_db()) as conn:
        rows = conn.execute(
            """
            SELECT id, filename, uploaded_at, extracted_text
            FROM reports
            ORDER BY uploaded_at DESC
            """
        ).fetchall()

    return [
        {
            "id": row["id"],
            "filename": row["filename"],
            "uploaded_at": row["uploaded_at"],
            "text_preview": row["extracted_text"][:300],
        }
        for row in rows
    ]


def get_report(report_id: int) -> Optional[dict]:
    """Return one report with its full extracted text, or None if not found."""
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ?",
            (report_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "filename": row["filename"],
        "uploaded_at": row["uploaded_at"],
        "extracted_text": row["extracted_text"],
    }


def get_all_report_texts() -> list[dict]:
    """Return filename and full text of every report (used by retrieval)."""
    with closing(get_db()) as conn:
        rows = conn.execute(
            "SELECT filename, extracted_text FROM reports"
        ).fetchall()

    return [
        {"filename": row["filename"], "extracted_text": row["extracted_text"]}
        for row in rows
    ]


def delete_report(report_id: int) -> bool:
    """
    Delete the stored DOCX file and the database record.
    Returns True if deleted, False if the report does not exist.
    """
    with closing(get_db()) as conn:
        with conn:
            row = conn.execute(
                "SELECT stored_filename FROM reports WHERE id = ?",
                (report_id,),
            ).fetchone()

            if row is None:
                return False

            file_path = UPLOAD_DIR / row["stored_filename"]
            if file_path.exists():
                file_path.unlink()

            conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))

    return True