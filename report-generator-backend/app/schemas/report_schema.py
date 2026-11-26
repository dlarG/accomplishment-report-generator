
from pydantic import BaseModel, Field
from typing import List, Optional


class AccomplishmentEntry(BaseModel):
    raw_text: str = Field(
        ...,
        min_length=1,
        description="Original accomplishment notes"
    )

    accomplishment: Optional[str] = None

    remarks: Optional[str] = ""


class ReportRequest(BaseModel):
    faculty_name: str = Field(..., min_length=1)

    program_head_name: str = Field(..., min_length=1)

    program_head_designation: str = "Program Head, BSIT"

    reporting_period: str = Field(..., min_length=1)

    instruction_subjects: str = Field(..., min_length=1)

    entries: List[AccomplishmentEntry] = Field(
        ...,
        min_length=1
    )
