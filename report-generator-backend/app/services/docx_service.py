
from io import BytesIO
from pathlib import Path
import re

from docx import Document


BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = (
    BASE_DIR
    / "app"
    / "templates"
    / "Monthly_Accomplishment_Report_Template.docx"
)


def _normalize_text(text: str) -> str:
    """Normalize text for comparing table headings and labels."""

    return re.sub(r"\s+", " ", text).strip().lower()


def _replace_in_paragraph(paragraph, replacements: dict):
    """Replace placeholders in a paragraph while retaining its first run."""

    original_text = paragraph.text
    updated_text = original_text

    for placeholder, value in replacements.items():
        updated_text = updated_text.replace(
            placeholder,
            str(value or "")
        )

    if updated_text != original_text:
        if paragraph.runs:
            paragraph.runs[0].text = updated_text

            for run in paragraph.runs[1:]:
                run.text = ""
        else:
            paragraph.add_run(updated_text)


def _replace_placeholders(document, replacements: dict):
    """Replace placeholders in paragraphs and table cells."""

    for paragraph in document.paragraphs:
        _replace_in_paragraph(paragraph, replacements)

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    _replace_in_paragraph(paragraph, replacements)


def _set_labeled_value(document, labels: list[str], value: str):
    """
    Fill a value beside a matching label.

    Supports labels such as:
        Month: __________
        Faculty Name: __________

    Also supports a label in one table cell with its value
    in the next cell.
    """

    if not value:
        return

    normalized_labels = {
        _normalize_text(label)
        for label in labels
    }

    # Check ordinary paragraphs.
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        for label in normalized_labels:
            pattern = rf"^{re.escape(label)}\s*:\s*.*$"

            if re.match(pattern, _normalize_text(text)):
                prefix = text.split(":", 1)[0]
                paragraph.text = f"{prefix}: {value}"
                return

    # Check table cells.
    for table in document.tables:
        for row in table.rows:
            cells = row.cells

            for index, cell in enumerate(cells):
                cell_text = _normalize_text(cell.text)

                for label in normalized_labels:
                    if cell_text.rstrip(":") == label.rstrip(":"):
                        if index + 1 < len(cells):
                            cells[index + 1].text = value
                        else:
                            cell.text = f"{cell.text}: {value}"
                        return

                    if cell_text.startswith(label + ":"):
                        original_label = cell.text.split(":", 1)[0]
                        cell.text = f"{original_label}: {value}"
                        return


def _find_accomplishment_table(document):
    """Find the table containing DATE, ACCOMPLISHMENT, REMARKS."""

    for table in document.tables:
        if not table.rows:
            continue

        for row_index, row in enumerate(table.rows):
            headings = [
                _normalize_text(cell.text)
                for cell in row.cells
            ]

            has_date = any(
                heading == "date" for heading in headings
            )
            has_accomplishment = any(
                "accomplishment" in heading for heading in headings
            )
            has_remarks = any(
                "remarks" in heading for heading in headings
            )

            if has_date and has_accomplishment and has_remarks:
                return table, row_index

    raise ValueError(
        "Could not find the accomplishment table. "
        "Expected columns: DATE, ACCOMPLISHMENT, REMARKS."
    )


def _remove_table_rows_after_header(table, header_index: int):
    """Keep the header and remove existing sample/blank data rows."""

    for row in list(table.rows)[header_index + 1:]:
        table._tbl.remove(row._tr)


def _entry_value(entry, key, default=""):
    """Read a value from either a dictionary or Pydantic model."""

    if isinstance(entry, dict):
        return entry.get(key, default) or default

    return getattr(entry, key, default) or default


def generate_report_docx(report_data: dict) -> BytesIO:
    """
    Populate the official SLSU Monthly Accomplishment Report template.

    Expected report_data:
        faculty_name
        program_head_name
        program_head_designation
        reporting_period
        instruction_subjects
        entries
    """

    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Report template not found: {TEMPLATE_PATH}"
        )

    document = Document(TEMPLATE_PATH)

    # Values supplied by the user.
    faculty_name = report_data.get("faculty_name", "")
    program_head_name = report_data.get("program_head_name", "")
    program_head_designation = report_data.get(
        "program_head_designation", ""
    )
    reporting_period = report_data.get("reporting_period", "")
    instruction_subjects = report_data.get(
        "instruction_subjects", ""
    )
    entries = report_data.get("entries", [])

    if not entries:
        raise ValueError(
            "At least one accomplishment entry is required."
        )

    # Replace explicit placeholders if they exist in the template.
    replacements = {
        "{{FACULTY_NAME}}": faculty_name,
        "{{PROGRAM_HEAD_NAME}}": program_head_name,
        "{{PROGRAM_HEAD_DESIGNATION}}": program_head_designation,
        "{{REPORTING_PERIOD}}": reporting_period,
        "{{INSTRUCTION_SUBJECTS}}": instruction_subjects,
    }

    _replace_placeholders(document, replacements)

    # Fill common label-based fields where possible.
    _set_labeled_value(
        document,
        ["Month", "Reporting Period"],
        reporting_period
    )

    _set_labeled_value(
        document,
        ["Faculty Name", "Prepared by"],
        faculty_name
    )

    _set_labeled_value(
        document,
        ["Program Head", "Approved by"],
        program_head_name
    )

    _set_labeled_value(
        document,
        ["Instruction", "Subjects"],
        instruction_subjects
    )

    # Find the accomplishment table.
    table, header_index = _find_accomplishment_table(document)

    if len(table.rows[header_index].cells) < 3:
        raise ValueError(
            "The accomplishment table must have at least 3 columns."
        )

    # Keep the header row and remove existing sample rows.
    _remove_table_rows_after_header(table, header_index)

    # Add one row per accomplishment.
    for entry in entries:
        row = table.add_row()

        accomplishment = _entry_value(
            entry,
            "accomplishment"
        )

        remarks = _entry_value(
            entry,
            "remarks"
        )

        if not accomplishment:
            accomplishment = _entry_value(
                entry,
                "raw_text"
            )

        row.cells[0].text = ""
        row.cells[1].text = accomplishment
        row.cells[2].text = remarks

    # Merge the DATE column across all accomplishment rows.
    first_data_row = header_index + 1
    last_data_row = len(table.rows) - 1

    if last_data_row >= first_data_row:
        date_cell = table.cell(first_data_row, 0).merge(
            table.cell(last_data_row, 0)
        )
        date_cell.text = reporting_period

    # Return the generated document in memory.
    output = BytesIO()
    document.save(output)
    output.seek(0)

    return output
