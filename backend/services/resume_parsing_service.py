"""
Service module for parsing resume text using an external LLM API.

This module contains functions to extract structured data such as contact
information, work history, education, and skills from raw resume text.
It uses asynchronous calls to a third-party LLM and handles common issues
like malformed JSON output and API request failures.
"""

import os
import logging
import re
import uuid
import asyncio
from datetime import datetime, date
from typing import List, Optional

import json_repair
import requests
from pydantic import BaseModel, ValidationError, field_validator
from dateutil import parser

from sqlalchemy.orm import Session

# Import schemas from your project
from backend.schemas.applicant_schema import ApplicantCreate
from backend.schemas.application_schema import (
    Application,
    ApplicationCreate,
    ApplicationStatus,
    Certification,
    LanguageSkill,
)
from backend.schemas.work_experience_schema import WorkExperienceCreate
from backend.schemas.education_history_schema import EducationHistoryCreate

# --- New Imports for Database Interaction ---
from backend.crud import applicant_crud, application_crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLM API configuration
API_KEY = os.getenv("HVL_API_KEY")
API_URL = "https://aigateway.havelsan.com.tr/chat/v1/chat/completions"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# --- Internal Pydantic Schemas for Parsing Steps ---


class LLMInitialParseOutput(BaseModel):
    """
    Schema for the output of the first parsing stage:
    Extracts core contact info and raw text sections.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    github_profile_url: Optional[str] = None
    resume_language: Optional[str] = None
    sections: dict[str, Optional[str]]


class WorkExperienceOutput(BaseModel):
    """
    Pydantic schema to validate and parse work experience,
    handling various date string formats.
    """

    job_title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    @classmethod
    @field_validator("start_date", "end_date", mode="before")
    def parse_date_strings(cls, v, info):
        """
        Custom validator to handle date strings from LLM output.
        Combines a specific regex for `YYYY-YYYY` ranges with
        the robust `dateutil.parser` for other formats.
        """
        if not v or not isinstance(v, str):
            return None

        v_lower = v.lower().strip()

        # Step 1: Handle "present" and Turkish equivalents first
        if v_lower in ("present", "current", "halen", "devam ediyor"):
            return date.today()

        # Step 2: Handle "YYYY-YYYY" range with a dedicated regex
        range_match = re.match(r"^(\d{4})-(\d{4})$", v_lower)
        if range_match:
            start_year = int(range_match.group(1))
            end_year = int(range_match.group(2))

            if info.field_name == "start_date":
                return date(start_year, 1, 1)
            elif info.field_name == "end_date":
                return date(end_year, 12, 31)

        # Step 3: Use dateutil.parser for all other formats
        try:
            # dayfirst=True is specified to handle ambiguous European/Turkish formats
            # like 18-08-2022
            parsed_date = parser.parse(v_lower, dayfirst=True).date()
            return parsed_date
        except (parser.ParserError, ValueError, TypeError):
            # If dateutil can't figure it out, return None
            logger.warning(f"Could not parse date string: '{v}'")
            return None


class LLMWorkHistoryOutput(BaseModel):
    """
    Schema for the work history parsing stage.
    """

    work_experience: Optional[List[WorkExperienceOutput]] = []


class EducationHistoryOutput(BaseModel):
    """
    Pydantic schema to validate and parse education history,
    handling various date string formats.
    """

    degree: Optional[str] = None
    institution: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = None

    @classmethod
    @field_validator("start_date", "end_date", mode="before")
    def parse_date_strings(cls, v, info):
        """
        Custom validator to handle date strings from LLM output.
        Combines a specific regex for `YYYY-YYYY` ranges with
        the robust `dateutil.parser` for other formats.
        """
        if not v or not isinstance(v, str):
            return None

        v_lower = v.lower().strip()

        # Step 1: Handle "present" and Turkish equivalents first
        if v_lower in ("present", "current", "halen", "devam ediyor"):
            return date.today()

        # Step 2: Handle "YYYY-YYYY" range with a dedicated regex
        range_match = re.match(r"^(\d{4})-(\d{4})$", v_lower)
        if range_match:
            start_year = int(range_match.group(1))
            end_year = int(range_match.group(2))

            if info.field_name == "start_date":
                return date(start_year, 1, 1)
            elif info.field_name == "end_date":
                return date(end_year, 12, 31)

        # Step 3: Use dateutil.parser for all other formats
        try:
            # dayfirst=True is specified to handle ambiguous European/Turkish formats
            # like 18-08-2022
            parsed_date = parser.parse(v_lower, dayfirst=True).date()
            return parsed_date
        except (parser.ParserError, ValueError, TypeError):
            # If dateutil can't figure it out, return None
            logger.warning(f"Could not parse date string: '{v}'")
            return None


class LLMEducationHistoryOutput(BaseModel):
    """
    Schema for the education history parsing stage.
    """

    education_history: Optional[List[EducationHistoryOutput]] = []


class LLMSkillsOutput(BaseModel):
    """
    Schema for the output of the skills, certs, and languages parsing stage.
    """

    parsed_skills: Optional[List[str]] = []
    certifications: Optional[List[Certification]] = []
    languages: Optional[List[LanguageSkill]] = []


# --- Utility Functions ---


def _calculate_total_experience(work_experience: List[WorkExperienceCreate]) -> int:
    """
    Calculates the total work experience in full years, accounting for
    overlapping timeframes and various date formats.
    """
    if not work_experience:
        return 0

    all_month_years = set()

    for job in work_experience:
        try:
            # Convert date objects to datetime objects for calculation
            if job.start_date:
                start_dt = datetime.combine(job.start_date, datetime.min.time())
            else:
                continue

            if job.end_date:
                end_dt = datetime.combine(job.end_date, datetime.min.time())
            else:
                end_dt = datetime.now()

            if start_dt > end_dt:
                start_dt, end_dt = end_dt, start_dt

            current_date = start_dt.replace(day=1)
            while current_date <= end_dt:
                all_month_years.add((current_date.year, current_date.month))

                if current_date.month == 12:
                    current_date = current_date.replace(
                        year=current_date.year + 1, month=1
                    )
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        except Exception as e:
            logger.error("Error processing work experience date: %s", e)
            continue

    total_months = len(all_month_years)
    return int(total_months / 12)


async def _get_llm_response(payload: dict) -> Optional[dict]:
    """
    Handles API requests, retries, and fallbacks for LLM calls.
    Note: This is now an async function.
    """
    # Attempt primary API (Havelsan)
    havelsan_retries = 3
    for i in range(havelsan_retries):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            }
            logger.info("Attempt %s to connect to Havelsan API: %s", i + 1, API_URL)
            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            llm_output_json = response.json()
            content_str = llm_output_json.get("content")
            if not content_str:
                logger.error("Havelsan response JSON missing 'content' key.")
                break
            return _repair_llm_json(content_str)
        except requests.exceptions.RequestException as e:
            logger.error(
                "Havelsan request failed (Attempt %s/%s): %s. Retrying in %s seconds...",
                i + 1,
                havelsan_retries,
                e,
                2 ** (i + 1),
            )
            await asyncio.sleep(2 ** (i + 1))
        except Exception as e:
            logger.error("An unexpected error occurred during Havelsan call: %s", e)
            break

    # Fallback to Gemini API if primary fails
    if GEMINI_API_KEY:
        gemini_payload = {
            "contents": [{"parts": [{"text": payload["messages"][1]["content"]}]}],
            "generationConfig": {
                "temperature": 0.3,
            },
        }
        try:
            logger.info("Havelsan API failed. Attempting fallback to Gemini API.")
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=gemini_payload,
                timeout=10,
            )
            response.raise_for_status()
            gemini_output_json = response.json()
            content_str = gemini_output_json["candidates"][0]["content"]["parts"][0][
                "text"
            ]
            return _repair_llm_json(content_str)
        except requests.exceptions.RequestException as e:
            logger.error("Gemini fallback request failed: %s", e)
        except Exception as e:
            logger.error("An unexpected error occurred during Gemini fallback: %s", e)

    return None


def _repair_llm_json(output_str: str) -> Optional[dict]:
    """
    Repairs and parses an LLM's JSON output using a dedicated library.
    Handles extra text, markdown fences, and common syntax errors.
    """
    if not output_str:
        return None
    try:
        data = json_repair.repair_json(output_str, return_objects=True)
        return data
    except Exception as e:
        logger.error("JSON repair failed: %s", e)
        return None


# --- Step 1: Initial Parsing and Section Extraction ---


def _get_initial_parse_payload(text: str) -> dict:
    """
    Constructs a payload for the first LLM call, which extracts
    core contact info and raw section text.
    """
    initial_prompt = (
        "Extract the following information from the resume text: first name, "
        "last name, email, phone number, LinkedIn URL, GitHub URL, and the "
        "primary language of the resume ('en' or 'tr').\n\n"
        "Additionally, identify and return the raw text for the 'work history', "
        "'education history', and 'skills' sections. If a section is not found, "
        "its value should be `null`.\n\n"
        "Return the output as a single, strict JSON object with the following schema: "
        "{\n"
        '  "first_name": "string",\n'
        '  "last_name": "string",\n'
        '  "email": "string | null",\n'
        '  "phone_number": "string | null",\n'
        '  "linkedin_profile_url": "string | null",\n'
        '  "github_profile_url": "string | null",\n'
        '  "resume_language": "string",\n'
        '  "sections": {\n'
        '    "work_experience": "string | null",\n'
        '    "education_history": "string | null",\n'
        '    "skills": "string | null"\n'
        "  }\n"
        "}\n\n"
        "**Resume Text:**\n" + text
    )
    return {
        "model": "qwen2.5-coder:32b",
        "messages": [
            {
                "role": "system",
                "content": "You are a specialized parser that extracts contact info and resume sections. Respond only with the requested JSON.",
            },
            {"role": "user", "content": initial_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }


async def _parse_initial_info(raw_text: str) -> Optional[LLMInitialParseOutput]:
    """
    Step 1: Extracts applicant info and major sections.
    """
    payload = _get_initial_parse_payload(raw_text)
    data = await _get_llm_response(payload)
    if data:
        try:
            return LLMInitialParseOutput(**data)
        except ValidationError as e:
            logger.error("Pydantic validation failed for initial parse: %s", e)
    return None


# --- Step 2: Specialized Section Parsing ---


def _get_section_parse_payload(section_text: str, schema_description: str) -> dict:
    """
    Constructs a dynamic payload for parsing a specific section.
    """
    section_prompt = (
        f"Parse the following resume section text and extract all listed items. "
        f"Return the output as a single, strict JSON object. Do not include any "
        f"additional text or markdown fences (e.g., ```json).\n\n"
        f"**Schema:**\n{schema_description}\n\n"
        f"**Section Text:**\n{section_text}"
    )
    return {
        "model": "qwen2.5-coder:32b",
        "messages": [
            {
                "role": "system",
                "content": "You are a specialized parser for a single resume section. Respond only with the requested JSON object.",
            },
            {"role": "user", "content": section_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }


async def _parse_work_experience_section(
    section_text: str,
) -> List[WorkExperienceCreate]:
    """
    Parses a single work history section using a specialized prompt.
    """
    schema_desc = """
    {
      "work_experience": [
        {
          "job_title": "string",
          "company": "string",
          "start_date": "YYYY-MM | YYYY | YYYY-YYYY | 'present'",
          "end_date": "YYYY-MM | YYYY | YYYY-YYYY | 'present'",
          "description": "string | null"
        }
      ]
    }
    """
    payload = _get_section_parse_payload(section_text, schema_desc)
    data = await _get_llm_response(payload)
    if data and isinstance(data, dict):
        try:
            # Pydantic's validator will now handle the date string conversion
            validated_output = LLMWorkHistoryOutput(**data)
            return [
                WorkExperienceCreate(**item.model_dump())
                for item in validated_output.work_experience
            ]
        except ValidationError as e:
            logger.error("Pydantic validation failed for work history: %s", e)
    return []


async def _parse_education_section(section_text: str) -> List[EducationHistoryCreate]:
    """
    Parses a single education history section.
    """
    schema_desc = """
    {
      "education_history": [
        {
          "degree": "string",
          "institution": "string",
          "start_date": "YYYY-MM | YYYY | YYYY-YYYY | 'present'",
          "end_date": "YYYY-MM | YYYY | YYYY-YYYY | 'present'",
          "location": "string | null"
        }
      ]
    }
    """
    payload = _get_section_parse_payload(section_text, schema_desc)
    data = await _get_llm_response(payload)
    if data and isinstance(data, dict):
        try:
            # Pydantic's validator will now handle the date string conversion
            validated_output = LLMEducationHistoryOutput(**data)
            return [
                EducationHistoryCreate(**item.model_dump())
                for item in validated_output.education_history
            ]
        except ValidationError as e:
            logger.error("Pydantic validation failed for education history: %s", e)
    return []


async def _parse_skills_section(section_text: str) -> LLMSkillsOutput:
    """
    Parses skills, certifications, and languages from a section.
    """
    schema_desc = """
    {
      "parsed_skills": [ "string" ],
      "certifications": [
        {
          "name": "string",
          "year_issued": "string",
          "issuing_organization": "string | null"
        }
      ],
      "languages": [
        {
          "name": "string",
          "level": "string | null"
        }
      ]
    }
    """
    payload = _get_section_parse_payload(section_text, schema_desc)
    data = await _get_llm_response(payload)
    if data and isinstance(data, dict):
        try:
            return LLMSkillsOutput(**data)
        except ValidationError as e:
            logger.error("Pydantic validation failed for skills: %s", e)
    return LLMSkillsOutput()  # Return an empty model on failure


# --- Main Orchestrator Function ---


async def process_and_persist_resume(
    raw_text: str,
    resume_file_path: str,
    job_id: uuid.UUID,
    db: Session,
) -> Optional[Application]:
    """
    Main orchestration function to parse resume and persist data.
    1. Extracts core applicant data and section text with a single LLM call.
    2. Passes the raw section text to specialized parsing functions.
    3. Assembles the final *Create schemas and persists them to the database.
    """
    # Step 1: Initial Parse
    initial_parse_result = await _parse_initial_info(raw_text)
    if not initial_parse_result:
        logger.error("Failed to perform initial resume parse.")
        return None

    # Step 2: Specialized Parsing
    work_experience: List[WorkExperienceCreate] = []
    if initial_parse_result.sections.get("work_experience"):
        work_experience = await _parse_work_experience_section(
            initial_parse_result.sections["work_experience"]
        )

    education_history: List[EducationHistoryCreate] = []
    if initial_parse_result.sections.get("education_history"):
        education_history = await _parse_education_section(
            initial_parse_result.sections["education_history"]
        )

    parsed_skills: List[str] = []
    certifications: List[Certification] = []
    languages: List[LanguageSkill] = []
    if initial_parse_result.sections.get("skills"):
        skills_output = await _parse_skills_section(
            initial_parse_result.sections["skills"]
        )
        parsed_skills = skills_output.parsed_skills
        certifications = skills_output.certifications
        languages = skills_output.languages

    # Step 3: Handle Applicant
    applicant_create = ApplicantCreate(
        first_name=initial_parse_result.first_name or "N/A",
        last_name=initial_parse_result.last_name or "N/A",
        email=initial_parse_result.email or f"no-email-{uuid.uuid4()}@example.com",
        phone_number=initial_parse_result.phone_number,
        linkedin_profile_url=initial_parse_result.linkedin_profile_url,
        github_profile_url=initial_parse_result.github_profile_url,
    )

    # Check for existing applicant and create if necessary
    db_applicant = applicant_crud.get_applicant_by_email(
        db, email=applicant_create.email
    )
    if not db_applicant:
        db_applicant = applicant_crud.create_applicant(db, applicant_create)

    # Step 4: Assemble and Persist the Application
    total_years_experience = _calculate_total_experience(work_experience)

    application_create = ApplicationCreate(
        job_id=job_id,
        applicant_id=db_applicant.applicant_id,
        resume_file_path=resume_file_path,
        resume_language=initial_parse_result.resume_language,
        total_years_experience=total_years_experience,
        work_experience=work_experience,
        education_history=education_history,
        parsed_skills=parsed_skills,
        certifications=certifications,
        languages=languages,
        parsed_resume_data=raw_text,
        status=ApplicationStatus.RECEIVED,
    )

    db_application = application_crud.create_application(db, application_create)
    return db_application
