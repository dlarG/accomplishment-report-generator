
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.schemas.report_schema import ReportRequest
from app.services.ollama_service import generate_accomplishment
from app.services.docx_service import generate_report_docx


router = APIRouter(
    prefix="/api",
    tags=["Report Generation"]
)


class AccomplishmentRequest(BaseModel):
    raw_text: str = Field(
        ...,
        min_length=1,
        description="Original faculty accomplishment notes"
    )


@router.post("/generate-accomplishment")
def generate_accomplishment_endpoint(
    request: AccomplishmentRequest
):
    """
    Rewrite one raw accomplishment note using the local AI model.
    """

    try:
        result = generate_accomplishment(request.raw_text)

        return {
            "accomplishment": result["accomplishment"],
            "remarks": result["remarks"]
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate accomplishment: {str(exc)}"
        ) from exc


@router.post("/generate-docx")
def generate_docx_endpoint(
    request: ReportRequest
):
    """
    Generate the completed Monthly Accomplishment Report
    using the official SLSU Word template.
    """

    try:
        report_data = request.dict()

        document_buffer = generate_report_docx(report_data)

        return StreamingResponse(
            document_buffer,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            headers={
                "Content-Disposition": (
                    'attachment; filename="Monthly_Accomplishment_Report.docx"'
                )
            }
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Word report: {str(exc)}"
        ) from exc
