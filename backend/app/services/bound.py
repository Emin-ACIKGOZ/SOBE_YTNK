import fitz  # PyMuPDF
import logging
from io import BytesIO
from starlette.concurrency import run_in_threadpool
import asyncio
import os
import tkinter as tk
from tkinter import filedialog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _process_pdf_sync(pdf_file: BytesIO, output_dir: str):
    """
    Synchronously processes a PDF to draw bounding boxes and save as JPGs.
    """
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for page_num, page in enumerate(doc):
            # Get text blocks with their bounding boxes
            blocks = page.get_text("blocks")
            
            # Draw a rectangle around each text block
            for block in blocks:
                rect = fitz.Rect(block[:4])
                page.draw_rect(rect, color=(1, 0, 0), width=1.5)  # Red color, 1.5-pixel width
            
            # Render the page to a Pixmap (an in-memory image)
            pix = page.get_pixmap()
            
            # Save the pixmap as a JPG file
            output_filename = os.path.join(output_dir, f"page_{page_num + 1}.jpg")
            pix.save(output_filename)
            
            logger.info(f"Saved {output_filename}")

        doc.close()
        
        return f"Successfully created JPGs with bounding boxes in '{output_dir}'"

    except Exception as e:
        logger.error(f"An unexpected error occurred during PDF processing: {e}")
        return f"Error: {e}"

async def process_pdf(pdf_file: BytesIO, output_dir: str) -> str:
    """
    Asynchronously processes a PDF file.
    """
    result_message = await run_in_threadpool(_process_pdf_sync, pdf_file, output_dir)
    return result_message

def select_pdf():
    """
    Opens a file dialog to select a PDF, then processes it.
    """
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )

    if file_path:
        with open(file_path, "rb") as file:
            pdf_data = BytesIO(file.read())
            
            # Define output directory based on the PDF's filename
            output_dir = os.path.splitext(os.path.basename(file_path))[0] + "_output"
            
            # Use a new event loop for the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(process_pdf(pdf_data, output_dir))
            
            print(f"\n--- Processing Result ---\n")
            print(result)

if __name__ == "__main__":
    # Create a simple Tkinter window
    root = tk.Tk()
    root.title("PDF Bounding Box Creator")
    root.geometry("350x100")

    # Create a button to select PDF
    btn_select_pdf = tk.Button(root, text="Select PDF to Process", command=select_pdf)
    btn_select_pdf.pack(pady=20)

    # Start the GUI
    root.mainloop()