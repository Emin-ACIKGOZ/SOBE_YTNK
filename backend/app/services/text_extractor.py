"""
Service to extract raw text from PDF files.
"""

from io import BytesIO
import pypdf
from starlette.concurrency import run_in_threadpool
import logging

# Configure logging for better error handling in a production environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _extract_text_sync(pdf_file: BytesIO) -> str:
    """
    Synchronous helper function to perform the blocking PDF text extraction.
    This function should be run in a separate thread.
    """
    try:
        # Create a PdfReader object from the BytesIO stream
        reader = pypdf.PdfReader(pdf_file)
        
        # Check if the PDF is encrypted and attempt to decrypt it
        if reader.is_encrypted:
            # Note: This attempts decryption with an empty password. 
            # In a real-world scenario, you might want to handle this case
            # more gracefully or return a specific error.
            reader.decrypt("")
        
        # Initialize an empty string to hold the extracted text
        full_text = ""
        
        # Loop through each page of the PDF and extract the text
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text
            
        return full_text
        
    except pypdf.errors.PdfReadError as e:
        logger.error(f"Failed to read PDF file: {e}")
        return ""
    except Exception as e:
        logger.error(f"An unexpected error occurred during text extraction: {e}")
        return ""

async def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    """
    Extracts all text from a PDF file efficiently and non-blockingly.

    This function offloads the synchronous I/O operations of the pypdf library
    to a separate thread using `run_in_threadpool`, ensuring the main event loop
    of the FastAPI application remains responsive.

    Args:
        pdf_file: A BytesIO object containing the PDF file data.

    Returns:
        A string containing all the extracted text from the PDF.
        Returns an empty string if extraction fails or the file is not a valid PDF.
    """
    # Offload the blocking PDF processing to a background thread
    # This is a key best practice for maintaining a non-blocking, efficient service.
    extracted_text = await run_in_threadpool(_extract_text_sync, pdf_file)
    
    return extracted_text
