import fitz  # PyMuPDF

def get_resume_text(pdf_path):
    """Extract text from a resume PDF file."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        return f"Error reading resume: {str(e)}"
    return text.strip()
