import os
import uuid
import json
import asyncio
from io import BytesIO
import tkinter as tk
from tkinter import filedialog, messagebox

from app.services.llm_resume_parser import process_resume_with_llm
from app.services.text_extractor import extract_text_from_pdf


async def process_file(file_path):
    """
    Reads a PDF, extracts text, processes it with the LLM parser,
    and saves the structured output to a text file.
    """
    try:
        # Read PDF as BytesIO
        with open(file_path, "rb") as f:
            pdf_bytes = BytesIO(f.read())

        # Extract text asynchronously
        extracted_text = await extract_text_from_pdf(pdf_bytes)

        if not extracted_text.strip():
            messagebox.showerror("Error", "No text could be extracted from the PDF.")
            return

        # Call the LLM parser with the extracted text and a dummy URL or file_path as a reference
        applicant, application = await process_resume_with_llm(
            extracted_text, resume_file_url=file_path
        )

        if not applicant or not application:
            messagebox.showerror("Error", "Failed to parse resume using LLM.")
            return

        # Convert the Application data to dict/json. Pydantic's .model_dump() handles this.
        output_dict = application.model_dump()

        # Convert UUID objects to strings before serialization.
        # This is necessary because the default json.dump() cannot handle UUIDs.
        if "application_id" in output_dict:
            output_dict["application_id"] = str(output_dict["application_id"])
        if "applicant_id" in output_dict:
            output_dict["applicant_id"] = str(output_dict["applicant_id"])

        # Convert datetime objects to strings
        if (
            "application_date" in output_dict
            and output_dict["application_date"] is not None
        ):
            output_dict["application_date"] = output_dict[
                "application_date"
            ].isoformat()

        # Save the JSON output to a .txt file adjacent to the PDF
        output_file = os.path.splitext(file_path)[0] + "_parsed_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_dict, f, indent=4, ensure_ascii=False)

        messagebox.showinfo("Success", f"Parsed output saved to:\n{output_file}")

    except FileNotFoundError:
        messagebox.showerror("Error", "Selected file was not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")


def select_pdf_and_process():
    """
    Opens a file dialog for the user to select a PDF and starts the processing.
    """
    file_path = filedialog.askopenfilename(
        title="Select a PDF Resume", filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return

    # Run the async processing in an event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_file(file_path))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("LLM Resume Parser Tester")
    root.geometry("300x100")

    btn = tk.Button(
        root, text="Select PDF Resume to Parse", command=select_pdf_and_process
    )
    btn.pack(pady=20)

    root.mainloop()
