"""
Service module for parsing resume text using an external LLM API.

This module contains functions to extract structured data such as contact
information, work history, education, and skills from raw resume text.
It uses asynchronous calls to a third-party LLM and handles common issues
like malformed JSON output and API request failures.
"""

import logging
from math import floor
import uuid
import json
import asyncio
import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

import json_repair
import requests

from backend.app.schemas.applicant_schema import Applicant
from backend.app.schemas.application_schema import (
    Application,
    ApplicationStatus,
    Certification,
    WorkExperience,
    EducationHistory,
    LanguageSkill,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLM API configuration
API_KEY = "hvl-jiQhjbBbwZHvUGRAa3TPlYsKq0U4ira2tI81lUIyk9kfPSf"
API_URL = "https://aigateway.havelsan.com.tr/chat/v1/chat/completions"


class LLMResumeOutput(BaseModel):
    """
    Internal Pydantic schema for parsing the LLM's JSON response.
    This schema is now updated to reflect that the LLM will not generate
    the raw text. The raw text is handled in the application logic.
    """

    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    github_profile_url: Optional[str] = None
    resume_language: str

    work_history: Optional[List[WorkExperience]] = []
    education_history: Optional[List[EducationHistory]] = []

    parsed_skills: Optional[List[str]] = []
    certifications: Optional[List[Certification]] = []
    languages: Optional[List[LanguageSkill]] = []
    # This field is now correctly set outside of the LLM call.


def _parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Robustly parses various date string formats into a datetime object.
    Handles 'Present' and common delimiters like /, ., and -.
    """
    if not date_str:
        return None

    date_str_lower = date_str.lower().strip()
    if date_str_lower in ("present", "current"):
        return datetime.now()

    # Pattern for yyyy-mm, yyyy/mm, yyyy.mm
    year_month_match = re.search(r"(\d{4})[\/\.\-]?(\d{1,2})", date_str)
    if year_month_match:
        try:
            year = int(year_month_match.group(1))
            month = int(year_month_match.group(2))
            return datetime(year, month, 1)
        except (ValueError, IndexError):
            pass

    # Pattern for mm-yyyy, mm/yyyy, mm.yyyy
    month_year_match = re.search(r"(\d{1,2})[\/\.\-]?(\d{4})", date_str)
    if month_year_match:
        try:
            month = int(month_year_match.group(1))
            year = int(month_year_match.group(2))
            return datetime(year, month, 1)
        except (ValueError, IndexError):
            pass

    # Pattern for yyyy alone
    year_only_match = re.search(r"(\d{4})", date_str)
    if year_only_match:
        try:
            year = int(year_only_match.group(1))
            return datetime(year, 1, 1)
        except (ValueError, TypeError):
            pass

    return None


def _calculate_total_experience(work_history: List[WorkExperience]) -> int:
    """
    Calculates the total work experience in full years, accounting for
    overlapping timeframes and various date formats.
    """
    if not work_history:
        return 0

    all_month_years = set()

    for job in work_history:
        try:
            start_date = _parse_date_string(job.start_date)
            end_date = _parse_date_string(job.end_date) or datetime.now()

            if start_date is None or end_date is None:
                continue

            if start_date > end_date:
                start_date, end_date = end_date, start_date

            current_date = start_date.replace(day=1)
            while current_date <= end_date:
                all_month_years.add((current_date.year, current_date.month))

                if current_date.month == 12:
                    current_date = current_date.replace(
                        year=current_date.year + 1, month=1
                    )
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        except Exception as e:
            print("Error processing work experience date: %s", e)
            continue

    total_months = len(all_month_years)
    return floor(total_months / 12)


def _get_llm_payload(text: str) -> dict:
    """
    Constructs the correct request payload for the LLM API,
    with a prompt that no longer requests the LLM to reproduce the raw text.
    """
    refined_prompt = (
        "Extract the following information from the provided resume text. "
        "The resume may be in either English or Turkish. Return the output as "
        "a single, strict JSON object. Do not include any additional text, "
        "explanations, or markdown fences (e.g., ```json).\n\n"
        "**Instructions:**\n"
        "- For any field where information is not found in the resume, the "
        "value must be set to `null`.\n"
        "- **For all dates (start_date, end_date):**\n"
        '- If the date indicates the position is ongoing i.e. "Present" (or '
        '"devam ediyor"), write "present" as the date.\n'
        '- If only the year is available (e.g., "2016"), use `01/yyyy` '
        '(e.g., "01/2016").\n'
        "- If the exact date is found, use the `mm/yyyy` format (e.g., "
        '"03/2006").\n'
        "- The `resume_language` field must be `'en'` for English or `'tr'` "
        "for Turkish, based on the primary language of the resume.\n\n"
        "{\n"
        '  "first_name": "string",\n'
        '  "last_name": "string",\n'
        '  "email": "string | null",\n'
        '  "phone_number": "string | null",\n'
        '  "linkedin_profile_url": "string | null",\n'
        '  "github_profile_url": "string | null",\n'
        '  "resume_language": "string",\n'
        '  "work_history": [\n'
        "    {\n"
        '      "job_title": "string",\n'
        '      "company": "string",\n'
        '      "start_date": "mm/yyyy",\n'
        '      "end_date": "mm/yyyy",\n'
        '      "description": "string | null"\n'
        "    }\n"
        "  ],\n"
        '  "education_history": [\n'
        "    {\n"
        '      "degree": "string",\n'
        '      "institution": "string",\n'
        '      "start_date": "mm/yyyy",\n'
        '      "end_date": "mm/yyyy",\n'
        '      "location": "string | null"\n'
        "    }\n"
        "  ],\n"
        '  "parsed_skills": [ "string" ],\n'
        '  "certifications": [\n'
        "    {\n"
        '      "name": "string",\n'
        '      "year_issued": "string",\n'
        '      "issuing_organization": "string | null"\n'
        "    }\n"
        "  ],\n"
        '  "languages": [\n'
        "    {\n"
        '      "name": "string",\n'
        '      "level": "string | null"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "**Resume Text:**\n" + text
    )

    data = {
        "model": "qwen2.5-coder:32b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a resume parser. Your task is to extract all relevant "
                    "information from the following raw resume text. The output must "
                    "be a single, valid JSON object that adheres to the specified "
                    "schema, without any additional text or formatting (like '```json')."
                ),
            },
            {"role": "user", "content": refined_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2048,
    }
    return data


def _repair_llm_json(output_str: str) -> Optional[dict]:
    """
    Repairs and parses an LLM's JSON output using a dedicated library.
    Handles extra text, markdown fences, and common syntax errors.
    """
    if not output_str:
        return None
    try:
        # The repair_json function handles all common LLM errors
        # and returns a valid Python object directly.
        data = json_repair.repair_json(output_str, return_objects=True)
        return data
    except Exception as e:
        # If the repair process fails, return None.
        logger.error("JSON repair failed: %s", e)
        return None


def _process_work_history_dates(
    work_history: List[WorkExperience],
) -> List[WorkExperience]:
    """
    Post-processes the work history list to convert 'present' dates into
    'mm/yyyy' format.
    """
    processed_history = []
    current_month_year = datetime.now().strftime("%m/%Y")
    for job in work_history:
        # Check if the start date is 'present', which should not happen
        # based on prompt, but as a safeguard
        if job.start_date and job.start_date.lower().strip() == "present":
            start_date_str = current_month_year
        else:
            start_date_str = job.start_date

        if job.end_date and job.end_date.lower().strip() == "present":
            end_date_str = current_month_year
        else:
            end_date_str = job.end_date

        processed_history.append(
            WorkExperience(
                job_title=job.job_title,
                company=job.company,
                start_date=start_date_str,
                end_date=end_date_str,
                description=job.description,
            )
        )
    return processed_history


async def process_resume_with_llm(
    raw_text: str, resume_file_url: str
) -> tuple[Optional[Applicant], Optional[Application]]:
    """
    Uses an LLM to process raw resume text and return structured Applicant
    and Application data. Updated to handle the new LLM output structure and
    manage the raw text locally.
    """
    payload = _get_llm_payload(raw_text)

    retries = 3
    for i in range(retries):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            }
            logger.info("Attempting to connect to: %s", API_URL)
            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            response.raise_for_status()

            llm_output_json = response.json()
            content_str = llm_output_json.get("content")
            if not content_str:
                logger.error("Response JSON missing 'content' key.")
                break

            # Use the robust repair function which returns a Python object
            llm_data = _repair_llm_json(content_str)
            if not llm_data:
                logger.error("JSON repair failed, received unrecoverable output.")
                break

            logger.info("Parsed LLM content JSON:\n%s", json.dumps(llm_data, indent=4))

            # The Pydantic model now aligns perfectly with the LLM's output
            llm_output = LLMResumeOutput(**llm_data)

            applicant_id = uuid.uuid4()
            application_id = uuid.uuid4()
            current_time = datetime.now()

            # Process work history dates to convert "present" to current date
            processed_work_history = _process_work_history_dates(
                llm_output.work_history
            )

            # Calculate total experience using the processed list
            total_years_experience = _calculate_total_experience(processed_work_history)

            applicant = Applicant(
                applicant_id=applicant_id,
                first_name=llm_output.first_name,
                last_name=llm_output.last_name,
                email=llm_output.email,
                phone_number=llm_output.phone_number,
                linkedin_profile_url=llm_output.linkedin_profile_url,
                github_profile_url=llm_output.github_profile_url,
            )

            application = Application(
                application_id=application_id,
                applicant_id=applicant_id,
                resume_file_url=resume_file_url,
                resume_language=llm_output.resume_language,
                total_years_experience=total_years_experience,
                work_history=processed_work_history,
                education_history=llm_output.education_history,
                parsed_skills=llm_output.parsed_skills,
                certifications=llm_output.certifications,
                languages=llm_output.languages,
                parsed_resume_data=raw_text,
                status=ApplicationStatus.RECEIVED,
                application_date=current_time,
            )

            return applicant, application

        except requests.exceptions.RequestException as e:
            logger.error(
                "Request failed: %s. Retrying in %s seconds...", e, 2 ** (i + 1)
            )
            await asyncio.sleep(2 ** (i + 1))
        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)
            break

    return None, None
