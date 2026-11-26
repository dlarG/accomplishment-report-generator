
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.database.connection import UPLOAD_DIR
from app.database.knowledge_repository import (
    add_report,
    get_all_reports,
    get_report,
    delete_report,
)
from app.services.document_service import extract_text_from_docx


router = APIRouter(
    prefix="/api/knowledge",
    tags=["Knowledge Base"]
)


@router.post("/upload")
async def upload_knowledge_document(
    file: UploadFile = File(...)
):
    """Upload and extract text from a historical DOCX report."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename was provided."
        )

    original_filename = Path(file.filename).name

    if Path(original_filename).suffix.lower() != ".docx":
        raise HTTPException(
            status_code=400,
            detail="Only DOCX files are supported."
        )

    stored_filename = f"{uuid4().hex}.docx"
    file_path = UPLOAD_DIR / stored_filename

    try:
        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        file_path.write_bytes(file_content)

        extracted_text = extract_text_from_docx(file_path)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text was found in the document."
            )

        report_id = add_report(
            filename=original_filename,
            stored_filename=stored_filename,
            extracted_text=extracted_text
        )

        return {
            "message": "Report uploaded successfully.",
            "id": report_id,
            "report_id": report_id,
            "filename": original_filename,
            "extracted_text": extracted_text
        }

    except HTTPException:
        if file_path.exists():
            file_path.unlink()
        raise

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(exc)}"
        ) from exc

    finally:
        await file.close()



@router.get("")
def list_knowledge_documents():
    """List all uploaded historical reports."""

    try:
        reports = get_all_reports()

        return [
            {
                "id": report["id"],
                "filename": report["filename"],
                "uploaded_at": report["uploaded_at"],
                "text_preview": (
                    get_report(report["id"]) or {}
                ).get("extracted_text", "")[:300]
            }
            for report in reports
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve reports: {str(exc)}"
        ) from exc



@router.get("/{report_id}")
def get_knowledge_document(report_id: int):
    """Retrieve one report and its extracted text."""

    report = get_report(report_id)

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Knowledge Base report not found."
        )

    return report


@router.delete("/{report_id}")
def remove_knowledge_document(report_id: int):
    """Delete a report and its associated uploaded DOCX file."""

    try:
        deleted = delete_report(report_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Knowledge Base report not found."
            )

        return {
            "message": "Report deleted successfully.",
            "report_id": report_id
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(exc)}"
        ) from exc
