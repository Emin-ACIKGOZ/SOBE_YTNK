import uuid
import os
import requests
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import EducationLevel
from app.schemas.applicants import Applicant, ApplicantCreate
from app.schemas.applications import Application, ApplicationBase, ApplicationStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLM API configuration
API_KEY = "API KEY HERE"  # Replace with your actual API key or use environment variables
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Helper function for converting string to enum
EDUCATION_LEVEL_MAP = {
    "none": EducationLevel.NONE,
    "high school": EducationLevel.HIGH_SCHOOL,
    "associate": EducationLevel.ASSOCIATE,
    "bachelors": EducationLevel.BACHELORS,
    "masters": EducationLevel.MASTERS,
    "doctorate": EducationLevel.DOCTORATE
}

class LLMResumeOutput(BaseModel):
    """
    Internal Pydantic schema for parsing the LLM's JSON response.
    """
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    github_profile_url: Optional[str] = None
    resume_language: str
    total_years_experience: int
    has_bachelors_degree: bool
    highest_education_level: str
    most_recent_job_title: Optional[str] = None
    most_recent_company: Optional[str] = None
    parsed_skills: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    parsed_resume_data: Any

def _get_llm_payload(text: str) -> dict:
    
    prompt = f"""
    You are a highly skilled resume parser. Your task is to extract all relevant information from the following raw resume text. The resume can be in English or Turkish.

    The raw text is jumbled and may be difficult to read. You must use your best judgment to accurately parse the information and provide it in the specified JSON format.

    Raw Resume Text:
    {text}
    """
    
    
    data = {
    "model": "qwen2.5-coder:32b", 
    "messages": [
        {
            "role": "system",
            "content":"You are a highly skilled resume parser. Your task is to extract all relevant information from the following raw resume text. The resume can be in English or Turkish."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "generate_sqlschema",
            "strict": "true",
        "schema": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "linkedin_profile_url": {"type": "string"},
                    "github_profile_url": {"type": "string"},
                    "resume_language": {"type": "string", "description": "Detect and return the primary language of the resume (e.g., 'en', 'tr')."},
                    "total_years_experience": {"type": "NUMBER"},
                    "has_bachelors_degree": {"type": "BOOLEAN"},
                    "highest_education_level": {"type": "string", "enum": ["None", "High School", "Associate", "Bachelors", "Masters", "Doctorate"]},
                    "most_recent_job_title": {"type": "string"},
                    "most_recent_company": {"type": "string"},
                    "parsed_skills": {"type": "ARRAY", "items": {"type": "string"}},
                    "certifications": {"type": "ARRAY", "items": {"type": "string"}},
                    "languages": {"type": "ARRAY", "items": {"type": "string"}},
                    "parsed_resume_data": {"type": "string", "description": "The entire raw text of the resume as a single string."}
                },
                "required": [
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "linkedin_profile_url",
                    "github_profile_url",
                    "resume_language",
                    "total_years_experience",
                    "has_bachelors_degree",
                    "highest_education_level",
                    "most_recent_job_title",
                    "most_recent_company",
                    "parsed_skills",
                    "certifications",
                    "languages",
                    "parsed_resume_data"
                ]
            }
        }
    },
    "temperature": 0.7,
    "max_tokens": 250,
    "stream": False
}
   
    return data

async def process_resume_with_llm(raw_text: str, resume_file_url: str) -> tuple[Applicant, Application]:
    """
    Uses an LLM to process raw resume text and return structured Applicant and Application data.
    """
    # 1. Pre-process the raw text for better LLM parsing
    cleaned_text = raw_text
    
    # 2. Prepare the LLM request
    payload = _get_llm_payload(cleaned_text)

    # 3. Call the LLM with exponential backoff
    retries = 3
    for i in range(retries):
        try:
            # Prepare headers with the API key
            headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer hvl-jiQhjbBbwZHvUGRAa3TPlYsKq0U4ira2tI81lUIyk9kfPSf'
            }

            response = requests.post(API_URL, headers=headers, json=json.dumps(payload))
            print("response: " response)
            # Log the final URL used for the request
            logger.info(f"Attempting to connect to: {response.request.url}")

            response.raise_for_status() # Raise HTTPError for bad responses
            llm_output_json = response.json()
            
            # The LLM output is a string within the JSON.
            llm_text_part = llm_output_json.get('candidates')[0].get('content').get('parts')[0].get('text')
            
            # Sanitize the output (sometimes LLMs add extra formatting)
            llm_text_part = llm_text_part.replace("```json", "").replace("```", "").strip()
            
            llm_data = json.loads(llm_text_part)

            # 4. Create Pydantic models from LLM output
            llm_output = LLMResumeOutput(**llm_data)

            # Generate IDs and timestamps
            applicant_id = uuid.uuid4()
            application_id = uuid.uuid4()
            current_time = datetime.now()

            # Create Applicant model
            applicant = Applicant(
                applicant_id=applicant_id,
                first_name=llm_output.first_name,
                last_name=llm_output.last_name,
                email=llm_output.email,
                phone_number=llm_output.phone_number,
                linkedin_profile_url=llm_output.linkedin_profile_url,
                github_profile_url=llm_output.github_profile_url
            )
            
            # Create Application model
            # Map the highest education level string to the enum
            education_level = EDUCATION_LEVEL_MAP.get(llm_output.highest_education_level.lower(), EducationLevel.NONE)
            
            application = Application(
                application_id=application_id,
                applicant_id=applicant_id,
                resume_file_url=resume_file_url,
                resume_language=llm_output.resume_language,
                total_years_experience=llm_output.total_years_experience,
                has_bachelors_degree=llm_output.has_bachelors_degree,
                highest_education_level=education_level,
                most_recent_job_title=llm_output.most_recent_job_title,
                most_recent_company=llm_output.most_recent_company,
                parsed_skills=llm_output.parsed_skills,
                certifications=llm_output.certifications,
                languages=llm_output.languages,
                parsed_resume_data=llm_output.parsed_resume_data,
                status=ApplicationStatus.RECEIVED,
                application_date=current_time
            )
            
            return applicant, application

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}. Retrying in {2**(i+1)} seconds...")
            await asyncio.sleep(2**(i+1))
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding failed: {e}. Raw LLM output: {response.text}")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            break
            
    return None, None
