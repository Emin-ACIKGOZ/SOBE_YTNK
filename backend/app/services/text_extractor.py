import fitz # This is PyMuPDF
import logging
from io import BytesIO
from starlette.concurrency import run_in_threadpool
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _extract_text_sync(pdf_file: BytesIO) -> str:
    """
    Synchronous helper function to perform the blocking PDF text extraction
    using PyMuPDF, including normalization.
    """
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        doc.close()
        
        # Normalize multiple spaces into a single space.
        full_text = re.sub(r' +', ' ', full_text)

        # Normalize bullet point followed by any combination of whitespace and newlines
        # to a single bullet point and a space.
        full_text = re.sub(r'([•*-])\s*\n\s*', r'\1 ', full_text)
        
        # Normalize multiple newlines with only whitespace in between.
        full_text = re.sub(r'(\n\s*){2,}', '\n', full_text).strip()
        
        return full_text
    
    except Exception as e:
        logger.error(f"An unexpected error occurred during PyMuPDF text extraction: {e}")
        return ""

async def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    """
    Extracts all text from a PDF file efficiently and non-blockingly
    by offloading the task to a threadpool.

    Args:
        pdf_file: A BytesIO object containing the PDF file data.

    Returns:
        A string containing all the extracted text from the PDF.
        Returns an empty string on failure.
    """
    extracted_text = await run_in_threadpool(_extract_text_sync, pdf_file)
    return extracted_text
