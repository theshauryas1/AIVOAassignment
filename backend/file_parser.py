"""
file_parser.py – Extract plain text from uploaded deviation documents.
Supports: PDF, DOCX, TXT, JPG/PNG (via basic text if Tesseract unavailable).
"""
import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_bytes(filename: str, content: bytes) -> str:
    """
    Detect file type from extension and extract text.
    Returns the extracted text string (may be empty on failure).
    """
    ext = Path(filename).suffix.lower()
    try:
        if ext == ".pdf":
            return _parse_pdf(content)
        elif ext == ".docx":
            return _parse_docx(content)
        elif ext in (".txt", ".csv"):
            return content.decode("utf-8", errors="replace")
        elif ext in (".jpg", ".jpeg", ".png"):
            return _parse_image(content)
        elif ext == ".xls" or ext == ".xlsx":
            return _parse_excel(content, ext)
        else:
            return content.decode("utf-8", errors="replace")
    except Exception as exc:
        logger.error("File parse failed for %s: %s", filename, exc)
        return ""


def _parse_pdf(content: bytes) -> str:
    """Extract text from PDF using PyMuPDF."""
    import fitz  # PyMuPDF

    doc = fitz.open(stream=content, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    doc.close()
    return "\n".join(pages)


def _parse_docx(content: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    from docx import Document

    doc = Document(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    # Also grab table content
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    paragraphs.append(cell.text.strip())
    return "\n".join(paragraphs)


def _parse_image(content: bytes) -> str:
    """
    Try OCR with pytesseract; fall back to a placeholder message
    if Tesseract is not installed (no crash for demo purposes).
    """
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(img)
    except Exception:
        return "[Image uploaded – OCR not available. Please paste the deviation text instead.]"


def _parse_excel(content: bytes, ext: str) -> str:
    """Extract cell text from XLS/XLSX using openpyxl."""
    try:
        import openpyxl

        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        rows = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                line = "\t".join(str(c) for c in row if c is not None)
                if line.strip():
                    rows.append(line)
        return "\n".join(rows)
    except Exception:
        return ""
