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
from langdetect import detect, LangDetectException

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
    Extracts raw text sections using a dedicated LLM call.
    """

    contact_info: Optional[str] = None
    summary: Optional[str] = None
    work_experience: Optional[str] = None
    education_history: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None
    languages: Optional[str] = None


class ContactInfoOutput(BaseModel):
    """
    Schema for the output of the dedicated contact info parsing stage.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    github_profile_url: Optional[str] = None
    resume_language: Optional[str] = None


class WorkExperienceOutput(BaseModel):
    """
    Pydantic schema to validate and parse work experience,
    ensuring compliance with database schema requirements.
    """

    # These fields are required by WorkExperienceCreate, so they must be present.
    job_title: str
    company: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    @field_validator("start_date", "end_date", mode="before")
    # pylint: disable=no-self-argument
    def parse_date_strings(cls, v, info):
        """
        Custom validator to handle date strings from LLM output,
        ensuring a 'date' object is always returned.
        """
        if not v or not isinstance(v, str):
            # For non-required fields, we return None. For required fields,
            # this will be caught by Pydantic later.
            return None

        v_lower = v.lower().strip()

        # Handle "present" and Turkish equivalents
        if v_lower in ("present", "current", "halen", "devam ediyor"):
            return date.today()

        # Handle "YYYY-YYYY" range with a dedicated regex
        range_match = re.match(r"^(\d{4})-(\d{4})$", v_lower)
        if range_match:
            year = int(range_match.group(1 if info.field_name == "start_date" else 2))
            # Return a date object for the first or last day of the year
            return (
                date(year, 1, 1)
                if info.field_name == "start_date"
                else date(year, 12, 31)
            )

        # Use dateutil.parser for all other formats
        try:
            # The .date() call is crucial to convert from datetime to date.
            return parser.parse(v_lower, dayfirst=True).date()
        except (parser.ParserError, ValueError, TypeError) as e:
            logger.warning("Could not parse date string: '%s'. Error: %s", v, e)
            # Raising a ValueError allows Pydantic to handle the validation error.
            raise ValueError(f"Invalid date format: '{v}'") from e


class LLMWorkHistoryOutput(BaseModel):
    """
    Schema for the work history parsing stage.
    """

    work_experience: Optional[List[WorkExperienceOutput]] = []


class EducationHistoryOutput(BaseModel):
    """
    Pydantic schema to validate and parse education history,
    ensuring compliance with database schema requirements.
    """

    # These fields are required by EducationHistoryCreate, so they must be present.
    degree: str
    institution: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = None

    @field_validator("start_date", "end_date", mode="before")
    # pylint: disable=no-self-argument
    def parse_date_strings(cls, v, info):
        """
        Custom validator to handle date strings from LLM output,
        ensuring a 'date' object is always returned.
        """
        if not v or not isinstance(v, str):
            return None

        v_lower = v.lower().strip()

        # Handle "present" and Turkish equivalents
        if v_lower in ("present", "current", "halen", "devam ediyor"):
            return date.today()

        # Handle "YYYY-YYYY" range with a dedicated regex
        range_match = re.match(r"^(\d{4})-(\d{4})$", v_lower)
        if range_match:
            year = int(range_match.group(1 if info.field_name == "start_date" else 2))
            return (
                date(year, 1, 1)
                if info.field_name == "start_date"
                else date(year, 12, 31)
            )

        # Use dateutil.parser for all other formats
        try:
            return parser.parse(v_lower, dayfirst=True).date()
        except (parser.ParserError, ValueError, TypeError) as e:
            logger.warning("Could not parse date string: '%s'. Error: %s", v, e)
            raise ValueError(f"Invalid date format: '{v}'") from e


class LLMEducationHistoryOutput(BaseModel):
    """
    Schema for the education history parsing stage.
    """

    education_history: Optional[List[EducationHistoryOutput]] = []


class LLMSkillsAndLanguagesOutput(BaseModel):
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
            if not job.start_date:
                continue

            start_dt = datetime.combine(job.start_date, datetime.min.time())

            # Use today's date if the end date is not available
            end_date_for_calc = job.end_date if job.end_date else date.today()
            end_dt = datetime.combine(end_date_for_calc, datetime.min.time())

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
        except (TypeError, ValueError) as e:
            logger.error("Error processing work experience date: %s", e)
            continue

    total_months = len(all_month_years)
    return int(total_months / 12)


async def _get_llm_response(payload: dict) -> Optional[dict]:
    """
    Handles API requests, retries, and fallbacks for LLM calls.
    Note: This is now an async function.
    """
    # Attempt primary API (Gemini)
    gemini_retries = 3
    for i in range(gemini_retries):
        try:
            gemini_payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": payload["messages"][0]["content"]
                                + "\n\n"
                                + payload["messages"][1]["content"]
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": payload.get("temperature", 0.3),
                },
            }
            logger.info(
                "Attempt %s to connect to Gemini API: %s", i + 1, GEMINI_API_URL
            )
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
            logger.error(
                "Gemini request failed (Attempt %s/%s): %s. "
                "Retrying in %s seconds...",
                i + 1,
                gemini_retries,
                e,
                2 ** (i + 1),
            )
            await asyncio.sleep(2 ** (i + 1))
        # json_repair library's exceptions should be caught more generically
        except Exception as e:
            logger.error(
                "An error occurred during JSON processing in Gemini primary: %s", e
            )
            break

    # Fallback to Havelsan API if primary fails
    if API_KEY:
        havelsan_retries = 3
        for i in range(havelsan_retries):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}",
                }
                logger.info("Gemini API failed. Attempting fallback to Havelsan API.")
                response = requests.post(
                    API_URL, headers=headers, json=payload, timeout=10
                )
                response.raise_for_status()
                llm_output_json = response.json()
                content_str = llm_output_json.get("content")
                if not content_str:
                    logger.error("Havelsan response JSON missing 'content' key.")
                    break
                return _repair_llm_json(content_str)
            except requests.exceptions.RequestException as e:
                logger.error(
                    "Havelsan request failed (Attempt %s/%s): %s. "
                    "Retrying in %s seconds...",
                    i + 1,
                    havelsan_retries,
                    e,
                    2 ** (i + 1),
                )
                await asyncio.sleep(2 ** (i + 1))
            # json_repair library's exceptions should be caught more generically
            except Exception as e:
                logger.error("An error occurred during JSON processing: %s", e)
                break
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


def _detect_resume_language(text: str) -> str:
    """
    Detects the dominant language of the resume text.
    Returns 'en' or 'tr'.
    """
    try:
        # Detect the language and return a simple code
        return detect(text)
    except LangDetectException:
        logger.warning("Could not detect resume language. Defaulting to 'en'.")
        return "en"


# --- Custom Prompts for Each Section ---

CONTACT_INFO_PROMPT = """
The resume is predominantly in {language_context}. Parse the following unstructured contact information text.
Identify the **first name**, **last name**, **email**, **phone number**, and **LinkedIn** and **GitHub** URLs.
The name is usually the first line. The email contains '@'. The phone number often starts with a '+' or a series of digits. If a field is not found, its value should be null. Return a strict JSON object with the specified schema.
"""

WORK_EXPERIENCE_PROMPT = """
The resume is predominantly in {language_context}. Parse the following work history text. Each entry must be a separate object in a JSON list. Identify the **job title**, **company**, **start date**, **end date**, and a **description**. 'Present', 'Current', or 'Halen' should be converted to a modern date. The description should capture the key responsibilities and achievements, which are often found in bullet points. Return a strict JSON object with a 'work_experience' key containing the list.
"""

EDUCATION_PROMPT = """
The resume is predominantly in {language_context}. Parse the following education history text. Each entry must be a separate object in a JSON list. Identify the **degree**, **institution**, **start date**, **end date**, and **location**. If an end date is not specified, it means the person is still studying. Return a strict JSON object with an 'education_history' key containing the list.
"""

SKILLS_AND_LANGUAGES_PROMPT = """
The resume is predominantly in {language_context}. Parse the following text and extract a list of skills, certifications, and languages.

A **skill** is an ability or proficiency (e.g., 'Python', 'SQL', 'Microsoft Office', 'Project Management').
A **certification** is a formal credential or attestation, often with an issuing body (e.g., 'PMP', 'AWS Certified Solutions Architect').
A **language** is a human language with an associated proficiency level.

Look for keywords that introduce these sections, such as 'Skills', 'Technical Skills', 'Core Competencies', 'Yetenekler', 'Beceriler' for skills; 'Certifications', 'Licenses', 'Sertifikalar', 'Belgeler' for certifications; and 'Languages', 'Diller' for languages.

Skills should be a simple list of strings. Certifications should be a list of objects containing the name, year issued, and issuing organization. If a certification has no year or organization, use null. Languages should be a list of objects with the language name and proficiency level (e.g., 'Fluent', 'Native', 'Intermediate').

Return a single, strict JSON object with 'parsed_skills', 'certifications', and 'languages' keys.
"""

# --- Step 1: Initial Parsing and Section Extraction ---


def _get_initial_parse_payload(text: str, language_context: str) -> dict:
    """
    Constructs a payload for the first LLM call, which now focuses solely
    on extracting and sectionalizing the resume content.
    """
    initial_prompt = (
        f"The resume is predominantly in {language_context}. Analyze the entire resume text and identify its major sections. "
        "Return the raw text for each section under a standardized key. "
        "If a section is not found, its value must be `null`.\n\n"
        "**Standardized Keys:**\n"
        "- `contact_info` (for name, email, phone, links)\n"
        "- `summary` (for professional summary or objective)\n"
        "- `work_experience`\n"
        "- `education_history`\n"
        "- `skills`\n"
        "- `certifications`\n"
        "- `languages`\n\n"
        "Return the output as a single, strict JSON object. Do not include "
        "any other text, explanations, or markdown fences (e.g., ```json).\n\n"
        "**Resume Text:**\n" + text
    )
    return {
        "model": "qwen2.5-coder:32b",
        "messages": [
            {
                "role": "system",
                "content": "You are a specialized resume section extractor. Respond only with the requested JSON.",
            },
            {"role": "user", "content": initial_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }


async def _parse_contact_info_section(
    section_text: str, language_context: str
) -> Optional[ContactInfoOutput]:
    """
    Parses a single contact info section using a specialized and hardened prompt.
    """
    schema_desc = """
    {
      "first_name": "string | null",
      "last_name": "string | null",
      "email": "string | null",
      "phone_number": "string | null",
      "linkedin_profile_url": "string | null",
      "github_profile_url": "string | null",
      "resume_language": "string | null"
    }
    """
    prompt = CONTACT_INFO_PROMPT.format(language_context=language_context)
    payload = _get_section_parse_payload(section_text, schema_desc, prompt)
    data = await _get_llm_response(payload)

    if data and isinstance(data, dict):
        try:
            return ContactInfoOutput(**data)
        except ValidationError as e:
            logger.error("Pydantic validation failed for contact info: %s", e)
    return None


async def _parse_initial_info(
    raw_text: str, language_context: str
) -> Optional[LLMInitialParseOutput]:
    """
    Step 1: Extracts applicant info and major sections.
    """
    payload = _get_initial_parse_payload(raw_text, language_context)
    data = await _get_llm_response(payload)
    if data:
        try:
            return LLMInitialParseOutput(**data)
        except ValidationError as e:
            logger.error("Pydantic validation failed for initial parse: %s", e)
    return None


# --- Step 2: Specialized Section Parsing ---


def _get_section_parse_payload(
    section_text: str, schema_description: str, prompt_text: str
) -> dict:
    """
    Constructs a dynamic payload for parsing a specific section.
    """
    section_prompt = (
        f"{prompt_text}\n\n"
        f"**Schema:**\n{schema_description}\n\n"
        f"**Section Text:**\n{section_text}"
    )
    return {
        "model": "qwen2.5-coder:32b",
        "messages": [
            {
                "role": "system",
                "content": "You are a specialized parser for a single resume section. "
                "Respond only with the requested JSON object.",
            },
            {"role": "user", "content": section_prompt},
        ],
        "temperature": 0.0,
        "max_tokens": 1024,
    }


async def _parse_work_experience_section(
    section_text: str, language_context: str
) -> List[WorkExperienceCreate]:
    """
    Parses a single work history section using a specialized prompt.
    """
    # Updated schema description for the LLM to reflect the non-optional fields
    schema_desc = """
    {
      "work_experience": [
        {
          "job_title": "string",
          "company": "string",
          "start_date": "YYYY-MM | YYYY | 'present'",
          "end_date": "YYYY-MM | YYYY | 'present'",
          "description": "string | null"
        }
      ]
    }
    """
    prompt = WORK_EXPERIENCE_PROMPT.format(language_context=language_context)
    payload = _get_section_parse_payload(section_text, schema_desc, prompt)
    data = await _get_llm_response(payload)

    parsed_experiences = []
    if data and isinstance(data, dict):
        try:
            # Pydantic will now validate for the non-optional fields
            validated_output = LLMWorkHistoryOutput(**data)
            for item in validated_output.work_experience:
                # Only add valid entries that meet the database schema requirements
                if item.job_title and item.company and item.start_date:
                    parsed_experiences.append(WorkExperienceCreate(**item.model_dump()))
                else:
                    logger.warning(
                        "Skipping work experience entry due to missing required "
                        "fields."
                    )
        except ValidationError as e:
            logger.error("Pydantic validation failed for work history: %s", e)
    return parsed_experiences


async def _parse_education_section(
    section_text: str, language_context: str
) -> List[EducationHistoryCreate]:
    """
    Parses a single education history section.
    """
    # Updated schema description for the LLM to reflect the non-optional fields
    schema_desc = """
    {
      "education_history": [
        {
          "degree": "string",
          "institution": "string",
          "start_date": "YYYY-MM | YYYY | 'present'",
          "end_date": "YYYY-MM | YYYY | 'present'",
          "location": "string | null"
        }
      ]
    }
    """
    prompt = EDUCATION_PROMPT.format(language_context=language_context)
    payload = _get_section_parse_payload(section_text, schema_desc, prompt)
    data = await _get_llm_response(payload)

    parsed_education = []
    if data and isinstance(data, dict):
        try:
            validated_output = LLMEducationHistoryOutput(**data)
            for item in validated_output.education_history:
                # Only add valid entries that meet the database schema requirements
                if item.degree and item.institution and item.start_date:
                    parsed_education.append(EducationHistoryCreate(**item.model_dump()))
                else:
                    logger.warning(
                        "Skipping education history entry due to missing required "
                        "fields."
                    )
        except ValidationError as e:
            logger.error("Pydantic validation failed for education history: %s", e)
    return parsed_education


async def _parse_skills_and_languages_section(
    section_text: str, language_context: str
) -> LLMSkillsAndLanguagesOutput:
    """
    Parses skills, certifications, and languages from a section using a combined prompt.
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
    prompt = SKILLS_AND_LANGUAGES_PROMPT.format(language_context=language_context)
    payload = _get_section_parse_payload(section_text, schema_desc, prompt)
    data = await _get_llm_response(payload)
    if data and isinstance(data, dict):
        try:
            return LLMSkillsAndLanguagesOutput(**data)
        except ValidationError as e:
            logger.error("Pydantic validation failed for skills: %s", e)
    return LLMSkillsAndLanguagesOutput()  # Return an empty model on failure


# --- Main Orchestrator Function ---


async def process_and_persist_resume(
    raw_text: str,
    resume_file_path: str,
    job_id: uuid.UUID,
    db: Session,
) -> Optional[Application]:
    """
    Main orchestration function to parse resume and persist data.
    1. Detects language and extracts section text with a single LLM call.
    2. Passes the raw section text to specialized parsing functions.
    3. Assembles the final *Create schemas and persists them to the database.
    """
    # Step 1: Language Detection
    detected_language = _detect_resume_language(raw_text)
    language_context = (
        "Turkish with some English words"
        if detected_language == "tr"
        else "English with some Turkish words"
    )

    # Step 2: Initial Parse - Sectionalization
    initial_parse_result = await _parse_initial_info(raw_text, language_context)
    if not initial_parse_result:
        logger.error("Failed to perform initial resume sectionalization.")
        return None

    # Step 3: Specialized Parsing for each section
    applicant_create: Optional[ApplicantCreate] = None
    contact_info_output: Optional[ContactInfoOutput] = None
    if initial_parse_result.contact_info:
        contact_info_output = await _parse_contact_info_section(
            initial_parse_result.contact_info, language_context
        )
        if contact_info_output:
            applicant_create = ApplicantCreate(
                first_name=contact_info_output.first_name or "N/A",
                last_name=contact_info_output.last_name or "N/A",
                email=contact_info_output.email
                or f"no-email-{uuid.uuid4()}@example.com",
                phone_number=contact_info_output.phone_number,
                linkedin_profile_url=contact_info_output.linkedin_profile_url,
                github_profile_url=contact_info_output.github_profile_url,
            )

    work_experience: List[WorkExperienceCreate] = []
    if initial_parse_result.work_experience:
        work_experience = await _parse_work_experience_section(
            initial_parse_result.work_experience, language_context
        )

    education_history: List[EducationHistoryCreate] = []
    if initial_parse_result.education_history:
        education_history = await _parse_education_section(
            initial_parse_result.education_history, language_context
        )

    parsed_skills: List[str] = []
    certifications: List[Certification] = []
    languages: List[LanguageSkill] = []

    # Consolidate skills, certs, and languages into a single parsing step
    combined_text = ""
    if initial_parse_result.skills:
        combined_text += initial_parse_result.skills + "\n"
    if initial_parse_result.certifications:
        combined_text += initial_parse_result.certifications + "\n"
    if initial_parse_result.languages:
        combined_text += initial_parse_result.languages

    if combined_text.strip():
        skills_output = await _parse_skills_and_languages_section(
            combined_text, language_context
        )
        parsed_skills = skills_output.parsed_skills
        certifications = skills_output.certifications
        languages = skills_output.languages

    # Step 4: Handle Applicant
    # If no contact info was parsed, create a placeholder applicant
    if not applicant_create:
        applicant_create = ApplicantCreate(
            first_name="N/A",
            last_name="N/A",
            email=f"no-email-{uuid.uuid4()}@example.com",
            phone_number=None,
            linkedin_profile_url=None,
            github_profile_url=None,
        )

    # Check for existing applicant and create if necessary
    db_applicant = applicant_crud.get_applicant_by_email(
        db, email=applicant_create.email
    )
    if not db_applicant:
        db_applicant = applicant_crud.create_applicant(db, applicant_create)

    # Step 5: Assemble and Persist the Application
    total_years_experience = _calculate_total_experience(work_experience)

    application_create = ApplicationCreate(
        job_id=job_id,
        applicant_id=db_applicant.applicant_id,
        resume_file_path=resume_file_path,
        resume_language=detected_language,
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
