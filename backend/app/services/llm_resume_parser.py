import logging
from math import floor
import uuid
import json
import asyncio
import re
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel

import json_repair
import requests

from app.schemas.applicants import Applicant
from app.schemas.applications import (
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
    Updated to match the new, more granular schema.
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
    parsed_resume_data: Any


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
            print(f"Error processing work experience date: {e}")
            continue

    total_months = len(all_month_years)
    return floor(total_months / 12)


def _get_llm_payload(text: str) -> dict:
    """
    Constructs the correct request payload for the LLM API,
    now instructing it to return structured lists for work, education, and languages.
    """
    data = {
        "model": "qwen2.5-coder:32b",
        "messages": [
            {
                "role": "system",
                "content": "You are a highly skilled resume parser. Your task is to extract all relevant information from the following raw resume text. The resume can be in English or Turkish. The output must be a single, valid JSON object that adheres to the specified schema, without any additional text or formatting (like '```json').",
            },
            {
                "role": "user",
                "content": f"""
                Extract the following information from the resume text below and return it as a JSON object:
                
                1.  **first_name**: The applicant's first name.
                2.  **last_name**: The applicant's last name.
                3.  **email**: The applicant's email address.
                4.  **phone_number**: The applicant's phone number.
                5.  **linkedin_profile_url**: The URL of the applicant's LinkedIn profile.
                6.  **github_profile_url**: The URL of the applicant's GitHub profile.
                7.  **resume_language**: The primary language of the resume (e.g., 'en', 'tr').
                8.  **work_history**: An array of objects. Each object should contain "job_title", "company", "start_date" (formatted as "mm/yyyy" or "yyyy" if no month is present), "end_date" (formatted as "mm/yyyy" or "yyyy" if no month is present), and "description" for all professional experiences listed.
                9.  **education_history**: An array of objects. Each object should contain "degree", "institution", "start_date", "end_date", and "location" for all education listed.
                10. **parsed_skills**: A list of technical and soft skills.
                11. **certifications**: An array of objects. Each object should contain the "name" of the certification, the "year_issued", and the "issuing_organization" if available.
                12. **languages**: An array of objects. Each object should contain the "name" of the language and its "level" of proficiency if proficiency is listed.
                13. **parsed_resume_data**: The entire raw text of the resume.

                **Resume Text:**
                {text}
                """,
            },
        ],
        "temperature": 0.7,
        "max_tokens": 250,
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
        logger.error(f"JSON repair failed: {e}")
        return None


async def process_resume_with_llm(
    raw_text: str, resume_file_url: str
) -> tuple[Optional[Applicant], Optional[Application]]:
    """
    Uses an LLM to process raw resume text and return structured Applicant and Application data.
    Updated to handle the new LLM output structure.
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
            response = requests.post(API_URL, headers=headers, json=payload)
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

            llm_output = LLMResumeOutput(**llm_data)

            applicant_id = uuid.uuid4()
            application_id = uuid.uuid4()
            current_time = datetime.now()

            total_years_experience = _calculate_total_experience(
                llm_output.work_history
            )

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
                work_history=llm_output.work_history,
                education_history=llm_output.education_history,
                parsed_skills=llm_output.parsed_skills,
                certifications=llm_output.certifications,
                languages=llm_output.languages,
                parsed_resume_data=llm_output.parsed_resume_data,
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
