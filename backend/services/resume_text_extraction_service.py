"""
Service module for extracting text from a PDF file using PyMuPDF.
It demonstrates synchronous I/O in an asynchronous environment by offloading
the PyMuPDF text extraction to a threadpool.
"""

import logging
import asyncio
import tkinter as tk
from tkinter import filedialog
from io import BytesIO

import fitz  # PyMuPDF
from starlette.concurrency import run_in_threadpool


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _extract_text_sync(pdf_file: BytesIO) -> str:
    """
    Synchronously extracts structured text from a PDF.
    This function is designed to run in a threadpool to avoid blocking the event loop.
    """
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        full_text = []

        for page in doc:
            # Extract text blocks with their bounding boxes (x0, y0, x1, y1) and block type.
            blocks = page.get_text("blocks")

            # Sort the blocks based on their y-coordinate (for vertical reading order)
            # and then x-coordinate (for horizontal reading order within the same line).
            # This is a robust way to preserve the reading order.
            blocks.sort(key=lambda block: (block[1], block[0]))

            page_text = []
            for block in blocks:
                # The fourth element of the block tuple is the text content
                text = block[4].strip()
                if text:
                    page_text.append(text)

            # Use two newlines to separate content from different blocks.
            full_text.append("\n\n".join(page_text))

        doc.close()

        return "\n\n".join(full_text)

    except Exception as e:
        logger.error(
            "An unexpected error occurred during PyMuPDF text extraction: %s", e
        )
        return ""


async def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    """
    Asynchronously extracts text from a PDF file.
    """
    extracted_text = await run_in_threadpool(_extract_text_sync, pdf_file)
    return extracted_text


def select_pdf():
    """
    Opens a file dialog to select a PDF, then extracts and prints its text.
    """
    file_path = filedialog.askopenfilename(
        title="Select a PDF file", filetypes=[("PDF files", "*.pdf")]
    )

    if file_path:
        with open(file_path, "rb") as file:
            pdf_data = BytesIO(file.read())

            # Use a new event loop for the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            extracted_text = loop.run_until_complete(extract_text_from_pdf(pdf_data))

            print("\n--- Extracted Text ---\n")
            print(extracted_text)


if __name__ == "__main__":
    # Create a simple Tkinter window
    root = tk.Tk()
    root.title("PDF Text Extractor")
    root.geometry("300x100")

    # Create a button to select PDF
    # The command is set to the function name without parentheses
    btn_select_pdf = tk.Button(root, text="Select PDF File", command=select_pdf)
    btn_select_pdf.pack(pady=20)

    # Start the GUI
    root.mainloop()
