
from pathlib import Path

from app.database.connection import get_db, UPLOAD_DIR


def add_report(
    filename: str,
    stored_filename: str,
    extracted_text: str
) -> int:
    """Save an uploaded report's information to the database."""

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO reports (
                filename,
                stored_filename,
                extracted_text
            )
            VALUES (?, ?, ?)
            """,
            (filename, stored_filename, extracted_text)
        )

        return cursor.lastrowid


def get_all_reports() -> list[dict]:
    """Retrieve all reports, newest first."""

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, filename, stored_filename, uploaded_at
            FROM reports
            ORDER BY uploaded_at DESC, id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]


def get_report(report_id: int) -> dict | None:
    """Retrieve one report, including its extracted text."""

    with get_db() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM reports
            WHERE id = ?
            """,
            (report_id,)
        ).fetchone()

        return dict(row) if row else None


def delete_report(report_id: int) -> bool:
    """
    Delete a report from the database and its associated
    uploaded DOCX file.

    Returns True if the report existed and was deleted.
    """

    with get_db() as conn:
        row = conn.execute(
            """
            SELECT stored_filename
            FROM reports
            WHERE id = ?
            """,
            (report_id,)
        ).fetchone()

        if not row:
            return False

        stored_filename = row["stored_filename"]

        conn.execute(
            "DELETE FROM reports WHERE id = ?",
            (report_id,)
        )

    # Delete the physical file after the database transaction.
    if stored_filename:
        file_path = (UPLOAD_DIR / stored_filename).resolve()

        # Prevent deleting files outside the uploads directory.
        if file_path.parent == UPLOAD_DIR.resolve() and file_path.is_file():
            file_path.unlink()

    return True
