
from pathlib import Path
from docx import Document


def extract_text_from_docx(file_path: str | Path) -> str:
    """
    Extract text from paragraphs and tables in a DOCX document.
    Returns the extracted content as a single string.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    if file_path.suffix.lower() != ".docx":
        raise ValueError("Only DOCX files are supported.")

    document = Document(file_path)
    extracted_content = []

    # Extract paragraphs
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            extracted_content.append(text)

    # Extract tables
    for table in document.tables:
        for row in table.rows:
            row_content = []

            for cell in row.cells:
                cell_text = cell.text.strip()

                if cell_text:
                    row_content.append(cell_text)

            if row_content:
                extracted_content.append(" | ".join(row_content))

    return "\n".join(extracted_content)
