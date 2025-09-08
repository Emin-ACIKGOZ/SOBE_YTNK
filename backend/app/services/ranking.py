# This module contains a set of functions to rank job applications based on a
# weighted ensemble of multiple scoring algorithms.

import math
import uuid
from typing import Dict, Set
from datetime import datetime, timedelta
from backend.app.services.application_generator import generate_test_applications
from sentence_transformers import SentenceTransformer, util
from backend.app.schemas.enums import EmploymentType, SeniorityLevel, EducationLevel
from backend.app.schemas.jobs import JobPosting
from backend.app.schemas.applications import Application

# --- Configuration Data Tables ---

DEFAULT_ENSEMBLE_WEIGHTS = {
    "semantic_similarity": 0.25,
    "skill_match": 0.20,
    "experience_relevance": 0.35,
    "education_fit": 0.10,
    "time_decay": 0.10,
}

SENTENCE_TRANSFORMER_MODEL = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)

SENIORITY_EXPERIENCE_CURVE = {
    SeniorityLevel.internship: {"midpoint": 0.5, "steepness": 3},
    SeniorityLevel.entry_level: {"midpoint": 2, "steepness": 2},
    SeniorityLevel.associate: {"midpoint": 4, "steepness": 1},
    SeniorityLevel.mid_senior_level: {"midpoint": 7, "steepness": 0.8},
    SeniorityLevel.director: {"midpoint": 12, "steepness": 0.6},
    SeniorityLevel.executive: {"midpoint": 18, "steepness": 0.4},
}

EDUCATION_RELEVANCE_THRESHOLD = 0.6

MAX_EDUCATION_DURATION = {
    EducationLevel.HIGH_SCHOOL: 4,
    EducationLevel.ASSOCIATE: 3,
    EducationLevel.BACHELORS: 6,
    EducationLevel.MASTERS: 3,
    EducationLevel.DOCTORATE: 4,
}

# --- Scoring Functions ---


def score_by_semantic_similarity(job: JobPosting, resume: Application) -> float:
    """
    Calculates a semantic similarity score using vector embeddings.
    """
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

    if not job_text or not resume_text:
        return 0.0

    job_embedding = SENTENCE_TRANSFORMER_MODEL.encode(job_text, convert_to_tensor=True)
    resume_embedding = SENTENCE_TRANSFORMER_MODEL.encode(
        resume_text, convert_to_tensor=True
    )

    cosine_score = util.cos_sim(job_embedding, resume_embedding).item()
    return float(cosine_score)


def score_by_skill_match(job: JobPosting, resume: Application) -> float:
    """
    Calculates a score based on the overlap of required skills and certifications.
    """
    job_skills = {skill.lower() for skill in job.required_skills}
    resume_skills = {skill.lower() for skill in resume.parsed_skills}

    if not job_skills:
        return 1.0

    matched_skills = len(job_skills.intersection(resume_skills))
    skill_score = matched_skills / len(job_skills)

    job_cert_quals = {
        q.lower() for q in job.qualifications if "certificate" in q.lower()
    }
    resume_certs = {c.name.lower() for c in resume.certifications}
    matched_certs = len(job_cert_quals.intersection(resume_certs))

    cert_bonus = 0.0
    if job_cert_quals:
        cert_bonus = min(matched_certs / len(job_cert_quals), 0.2)

    return min(skill_score + cert_bonus, 1.0)


def score_by_relevant_experience(job: JobPosting, resume: Application) -> float:
    """
    Evaluates years of experience using a sigmoid function and
    multiplies by a relevance bonus based on job title semantic similarity.
    """
    job_title = job.title
    total_years_experience = resume.total_years_experience
    seniority_level = job.seniority_level

    config = SENIORITY_EXPERIENCE_CURVE.get(seniority_level)
    if not config:
        return 0.0

    x_val = total_years_experience
    midpoint = config["midpoint"]
    steepness = config["steepness"]

    # Sigmoid function for base experience score
    experience_score = 1 / (1 + math.exp(-steepness * (x_val - midpoint)))

    # Calculate relevance bonus (on a 0.0 to 1.0 scale)
    relevance_bonus = 0.0
    job_title_embedding = SENTENCE_TRANSFORMER_MODEL.encode(
        job_title, convert_to_tensor=True
    )

    for work_exp in resume.work_history:
        if not work_exp.job_title:
            continue

        work_title_embedding = SENTENCE_TRANSFORMER_MODEL.encode(
            work_exp.job_title, convert_to_tensor=True
        )
        similarity = util.cos_sim(job_title_embedding, work_title_embedding).item()

        relevance_bonus = max(relevance_bonus, similarity)

    # Normalize by multiplying the base score by the relevance bonus
    return experience_score * relevance_bonus


def score_by_education_fit(job: JobPosting, resume: Application) -> float:
    """
    Scores based on education relevance (via semantic matching) and duration.
    """
    job_title_embedding = SENTENCE_TRANSFORMER_MODEL.encode(
        job.title, convert_to_tensor=True
    )

    education_score = 0.0
    for edu in resume.education_history:
        try:
            edu_end_date = datetime.strptime(edu.end_date, "%m/%Y")
            edu_start_date = datetime.strptime(edu.start_date, "%m/%Y")
            duration_years = (edu_end_date - edu_start_date).days / 365.25
        except (ValueError, TypeError):
            continue

        edu_embedding = SENTENCE_TRANSFORMER_MODEL.encode(
            f"{edu.degree} {edu.institution}", convert_to_tensor=True
        )
        relevance_similarity = util.cos_sim(job_title_embedding, edu_embedding).item()

        if relevance_similarity > EDUCATION_RELEVANCE_THRESHOLD:
            edu_level = EducationLevel(edu.degree)
            max_years = MAX_EDUCATION_DURATION.get(edu_level)

            if max_years and duration_years > max_years:
                education_score -= 0.5
            else:
                education_score += relevance_similarity

    return max(0.0, min(education_score, 1.0))


def score_by_time_decay(resume: Application) -> float:
    """
    Applies a time-based decay to a resume's score based on the recency of experience.
    """
    reference_date = datetime.now()
    total_recency_score = 0
    total_duration_years = 0
    decay_rate = 0.15

    for job_experience in resume.work_history:
        try:
            start_date = datetime.strptime(job_experience.start_date, "%m/%Y")
            if job_experience.end_date and job_experience.end_date.lower() != "present":
                end_date = datetime.strptime(job_experience.end_date, "%m/%Y")
            else:
                end_date = reference_date

            duration_days = (end_date - start_date).days
            duration_years = duration_days / 365.25
            total_duration_years += duration_years

            midpoint_date = start_date + timedelta(days=duration_days / 2)
            years_ago = (reference_date - midpoint_date).days / 365.25

            recency_multiplier = math.exp(-decay_rate * years_ago)
            total_recency_score += duration_years * recency_multiplier
        except (ValueError, TypeError):
            continue

    return (
        total_recency_score / total_duration_years if total_duration_years > 0 else 0.0
    )


# --- Ensemble Function ---


def calculate_ensemble_score(
    job: JobPosting, resume: Application, weights: Dict[str, float] = None
) -> float:
    """
    Calculates a final ensemble score by combining multiple ranking algorithms.
    """
    if weights is None:
        weights = DEFAULT_ENSEMBLE_WEIGHTS

    semantic_score = score_by_semantic_similarity(job, resume)
    skill_score = score_by_skill_match(job, resume)
    experience_score = score_by_relevant_experience(job, resume)
    education_score = score_by_education_fit(job, resume)
    time_decay_score = score_by_time_decay(resume)

    # Ensure scores are within the valid [0, 1] range
    semantic_score = max(0.0, min(semantic_score, 1.0))
    education_score = max(0.0, min(education_score, 1.0))

    final_score = (
        weights["semantic_similarity"] * semantic_score
        + weights["skill_match"] * skill_score
        + weights["experience_relevance"] * experience_score
        + weights["education_fit"] * education_score
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
