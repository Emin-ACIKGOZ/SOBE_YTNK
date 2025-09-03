import fitz  # PyMuPDF
import logging
from io import BytesIO
from starlette.concurrency import run_in_threadpool
import re
import tkinter as tk
from tkinter import filedialog
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your existing functions here (e.g., _extract_text_sync, extract_text_from_pdf)

def _extract_text_sync(pdf_file: BytesIO) -> str:
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        doc.close()
        
        # Normalize multiple spaces into a single space.
        full_text = re.sub(r' +', ' ', full_text)

        # Normalize bullet point followed by any combination of whitespace and newlines
        full_text = re.sub(r'([•*-])\s*\n\s*', r'\1 ', full_text)

        # Normalize multiple newlines with only whitespace in between.
        full_text = re.sub(r'(\n\s*){2,}', '\n', full_text).strip()
        
        return full_text
    
    except Exception as e:
        logger.error(f"An unexpected error occurred during PyMuPDF text extraction: {e}")
        return ""

async def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    extracted_text = await run_in_threadpool(_extract_text_sync, pdf_file)
    return extracted_text

def select_pdf(file_path):
    # Create a file dialog to select the PDF file
    # file_path = filedialog.askopenfilename(
    #     title="Select a PDF File",
    #     filetypes=[("PDF Files", "*.pdf")]
    # )
    
    if file_path:
        with open(file_path, "rb") as file:
            pdf_data = BytesIO(file.read())
            # Run the async function and retrieve the extracted text
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            extracted_text = loop.run_until_complete(extract_text_from_pdf(pdf_data))
            print(extracted_text)

if __name__ == "__main__":
    # Create a simple Tkinter window
    root = tk.Tk()
    root.title("PDF Text Extractor")
    root.geometry("300x100")

    # Create a button to select PDF
    btn_select_pdf = tk.Button(root, text="Select PDF File", command=select_pdf)
    btn_select_pdf.pack(pady=20)

    # Start the GUI
    root.mainloop()