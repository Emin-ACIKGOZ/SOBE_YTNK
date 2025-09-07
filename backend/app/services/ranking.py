"""
This module contains a set of functions to rank job applications based on a
weighted ensemble of multiple scoring algorithms.
"""

import math
import uuid
from typing import Dict, Set
from datetime import datetime, timedelta

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.enums import EmploymentType, SeniorityLevel
from app.services.application_generator import generate_test_applications
from app.schemas.jobs import JobPosting
from app.schemas.applications import Application

# Define the updated weights for the ensemble score to prioritize work experience
DEFAULT_ENSEMBLE_WEIGHTS = {
    "keywords": 0.20,  # A scaled, but still important factor for required skills
    "cosine_similarity": 0.15,  # Semantic similarity of job description and resume
    "skill_gap": 0.30,  # Still important for penalizing missing skills
    "experience_level": 0.25,  # Increased to significantly prioritize seniority and relevance
    "time_decay": 0.10,  # Increased to reward recent experience
}


def score_by_keywords(job: JobPosting, resume: Application) -> float:
    """
    Scores a resume based on the presence of required keywords from a job posting.
    The score is now normalized between 0.0 and 1.0.

    Args:
        job: The JobPosting Pydantic object.
        resume: The Application Pydantic object.

    Returns:
        A float score (0.0 to 1.0) based on normalized keyword matches.
    """
    job_skills = {skill.lower() for skill in job.required_skills}
    resume_skills = {skill.lower() for skill in resume.parsed_skills}

    # Calculate the number of matched skills
    matched_skills = len(job_skills.intersection(resume_skills))
    total_required_skills = len(job_skills)

    # Base score is the percentage of skills matched
    skill_score = (
        matched_skills / total_required_skills if total_required_skills > 0 else 0.0
    )

    # Optional: Add a bonus for relevant certifications, normalized
    job_cert_qualifications = {
        qual.lower() for qual in job.qualifications if "certificate" in qual.lower()
    }
    resume_certifications = {cert.name.lower() for cert in resume.certifications}
    matched_certs = len(job_cert_qualifications.intersection(resume_certifications))

    cert_bonus = 0.0
    if len(job_cert_qualifications) > 0:
        cert_bonus = min(
            matched_certs / len(job_cert_qualifications), 0.2
        )  # Cap bonus at 0.2

    # Final score is capped at 1.0
    return min(skill_score + cert_bonus, 1.0)


def score_by_tfidf_cosine_similarity(job: JobPosting, resume: Application) -> float:
    """
    Calculates a semantic similarity score using TF-IDF and Cosine Similarity.

    Args:
        job: The JobPosting Pydantic object.
        resume: The Application Pydantic object.

    Returns:
        A float score (0.0 to 1.0) representing semantic similarity.
    """
    # Create a single document for the job posting from multiple fields
    job_text = " ".join(
        [
            job.title,
            job.description,
            " ".join(job.required_skills),
            " ".join(job.qualifications),
            " ".join(job.responsibilities),
        ]
    )

    resume_text = str(resume.parsed_resume_data) if resume.parsed_resume_data else ""

    documents = [job_text, resume_text]

    if not any(documents):
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Cosine similarity between the two vectors
    cosine_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return float(cosine_score[0][0])


def score_by_time_decay(
    resume: Application, decay_rate: float = 0.15, reference_date: datetime = None
) -> float:
    """
    Applies a time-based decay to a resume's score based on the recency of experience.

    Args:
        resume: The Application Pydantic object.
        decay_rate: A float controlling how quickly the score decays over time.
        reference_date: The date to calculate recency from. Defaults to today.

    Returns:
        A float score (0.0 to 1.0) representing recency.
    """
    if reference_date is None:
        reference_date = datetime.now()

    total_recency_score = 0
    total_duration_years = 0

    # Calculate score based on work history recency
    for job_experience in resume.work_history:
        try:
            start_date_str = job_experience.start_date
            end_date_str = job_experience.end_date

            if not start_date_str:
                continue

            # Parse start date and end date
            start_date = datetime.strptime(start_date_str, "%m/%Y")
            if end_date_str and end_date_str.lower() != "present":
                end_date = datetime.strptime(end_date_str, "%m/%Y")
            else:
                end_date = reference_date

            # Calculate job duration in years and midpoint
            duration_days = (end_date - start_date).days
            duration_years = duration_days / 365.25
            total_duration_years += duration_years

            midpoint_date = start_date + timedelta(days=duration_days / 2)
            years_ago = (reference_date - midpoint_date).days / 365.25

            # Apply exponential decay
            recency_multiplier = math.exp(-decay_rate * years_ago)
            total_recency_score += duration_years * recency_multiplier
        except (ValueError, TypeError):
            continue

    if total_duration_years == 0:
        return 0.0

    # Normalize the score
    return total_recency_score / total_duration_years


def score_by_experience_level(job: JobPosting, resume: Application) -> float:
    """
    Scores a resume based on a rule-based evaluation of experience level.
    The score is now normalized between 0.0 and 1.0 and considers job title relevance.

    Args:
        job: The JobPosting Pydantic object.
        resume: The Application Pydantic object.

    Returns:
        A float score (0.0 to 1.0) representing the fit for the required seniority and experience.
    """
    calculated_score = 0.0
    total_years_experience = resume.total_years_experience
    seniority_level = job.seniority_level.value.lower()

    # Define a maximum possible score for normalization
    max_score = 3.0  # Base (1.0) + relevance (1.0) + education/certs (1.0)

    # 1. Score based on years of experience and seniority level
    if seniority_level == "junior":
        if total_years_experience >= 1:
            calculated_score += 1.0
        elif total_years_experience >= 3:
            calculated_score += 1.5
    elif seniority_level == "mid-senior_level":  # This corresponds to 'Kıdemli'
        if total_years_experience >= 3:
            calculated_score += 0.5
        if total_years_experience >= 7:
            calculated_score += 1.0
    elif seniority_level == "senior":
        if total_years_experience >= 7:
            calculated_score += 1.0
        if total_years_experience >= 10:
            calculated_score += 1.5
    elif seniority_level == "executive":
        if total_years_experience >= 10:
            calculated_score += 1.0
        if total_years_experience >= 15:
            calculated_score += 1.5

    # 2. Add score for job title relevance
    job_title_keywords = {"python", "geliştirici", "yazılım"}
    relevance_score = 0.0
    for job_experience in resume.work_history:
        job_title = job_experience.job_title.lower()
        if any(keyword in job_title for keyword in job_title_keywords):
            relevance_score = 1.0
            break
    calculated_score += relevance_score

    # 3. Add score for relevant degrees and certifications
    required_quals = {qual.lower() for qual in job.qualifications}
    # Check for relevant degrees
    has_relevant_degree = any("degree" in qual for qual in required_quals)
    if has_relevant_degree and any(
        edu.degree.lower() for edu in resume.education_history
    ):
        calculated_score += 0.5

    # Check for certifications
    has_required_cert = any("certificate" in qual for qual in required_quals)
    if has_required_cert:
        resume_certs = {cert.name.lower() for cert in resume.certifications}
        if any(
            cert_name in qual for qual in required_quals for cert_name in resume_certs
        ):
            calculated_score += 0.5

    return min(calculated_score / max_score, 1.0)


def score_by_skill_gap(job: JobPosting, resume: Application) -> float:
    """
    Calculates a score based on the number of missing required skills.

    The score is normalized between 0.0 and 1.0, where 1.0 means no missing skills.

    Args:
        job: The JobPosting Pydantic object.
        resume: The Application Pydantic object.

    Returns:
        A float score (0.0 to 1.0).
    """
    job_required_skills: Set[str] = {skill.lower() for skill in job.required_skills}
    resume_skills: Set[str] = {skill.lower() for skill in resume.parsed_skills}

    if not job_required_skills:
        return 1.0  # No required skills, so no gaps.

    missing_skills = job_required_skills.difference(resume_skills)

    # The score is the inverse of the number of missing skills, normalized
    final_score = (len(job_required_skills) - len(missing_skills)) / len(
        job_required_skills
    )

    return final_score


def calculate_ensemble_score(
    job: JobPosting, resume: Application, weights: Dict[str, float] = None
) -> float:
    """
    Calculates a final ensemble score by combining multiple ranking algorithms with adjustable weights.

    Args:
        job: The JobPosting Pydantic object.
        resume: The Application Pydantic object.
        weights: A dictionary of weights for each scoring algorithm.

    Returns:
        A float representing the final ensemble score.
    """
    if weights is None:
        weights = DEFAULT_ENSEMBLE_WEIGHTS

    # Calculate individual scores
    keyword_score = score_by_keywords(job, resume)
    cosine_score = score_by_tfidf_cosine_similarity(job, resume)
    skill_gap_score = score_by_skill_gap(job, resume)
    experience_score = score_by_experience_level(job, resume)
    time_decay_score = score_by_time_decay(resume)

    # Calculate final ensemble score using the weighted formula
    final_score = (
        weights["keywords"] * keyword_score
        + weights["cosine_similarity"] * cosine_score
        + weights["skill_gap"] * skill_gap_score
        + weights["experience_level"] * experience_score
        + weights["time_decay"] * time_decay_score
    )

    return final_score


if __name__ == "__main__":
    # 1. Define the job posting for a Senior Python Developer in Turkish.
    # This is a realistic job description based on real-world examples.
    senior_python_job = JobPosting(
        job_id=uuid.uuid4(),
        posted_at=datetime.now(),
        is_active=True,
        title="Kıdemli Python Geliştiricisi",
        company_name="Innovate Teknoloji A.Ş.",
        location="İstanbul",
        seniority_level=SeniorityLevel.mid_senior_level,
        employment_type=EmploymentType.full_time,
        description="""
        Innovate Teknoloji A.Ş. olarak, ekibimize katılacak dinamik ve deneyimli bir Kıdemli Python Geliştiricisi arıyoruz. Adayların Python'ın derinlemesine bilgisine ve mikroservis mimarileri ile çalışma tecrübesine sahip olması beklenmektedir.
        """,
        responsibilities=[
            "Ölçeklenebilir web uygulamaları ve RESTful API'ler geliştirmek.",
            "Test otomasyonu ve sürekli entegrasyon süreçlerine katkıda bulunmak.",
            "Teknik gereksinimleri analiz etmek ve tasarım çözümleri sunmak.",
            "Ekip üyelerine mentorluk yapmak ve kod incelemeleri gerçekleştirmek.",
        ],
        qualifications=[
            "Bilgisayar Bilimleri veya ilgili bir alanda Lisans derecesi.",
            "En az 7 yıl profesyonel Python geliştirme deneyimi.",
        ],
        required_skills=[
            "Python",
            "Django",
            "Flask",
            "RESTful API",
            "Microservices",
            "SQLAlchemy",
            "Celery",
            "Docker",
            "Kubernetes",
            "AWS",
            "Git",
        ],
    )

    # 2. Generate 100 sample applications using the imported function
    print("100 adet örnek başvuru oluşturuluyor...")
    applications = generate_test_applications(100)

    # 3. Rank the applications
    print("Başvurular sıralanıyor...")
    ranked_applications = []
    for app in applications:
        score = calculate_ensemble_score(senior_python_job, app)
        # Store the full application object to be able to print its details later
        ranked_applications.append({"application": app, "score": score})

    # Sort in descending order by score
    ranked_applications.sort(key=lambda x: x["score"], reverse=True)

    # 4. Print results to ranking.txt
    print("Sonuçlar ranking.txt dosyasına yazılıyor.")
    with open("ranking.txt", "w", encoding="utf-8") as f:
        f.write("Başvuru Sıralama Sonuçları\n")
        f.write("---------------------------\n\n")
        for rank, result in enumerate(ranked_applications, 1):
            f.write(f"Sıra: {rank}\n")
            f.write(f"Başvuru ID: {result['application'].application_id}\n")
            f.write(f"Ensemble Skoru: {result['score']:.4f}\n")
            f.write("Başvuru Detayları:\n")
            f.write(result["application"].model_dump_json(indent=2))
            f.write("\n\n---------------------------\n")

    print("İşlem tamamlandı. Sonuçlar ranking.txt dosyasında bulunabilir.")
