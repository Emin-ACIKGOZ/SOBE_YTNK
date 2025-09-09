"""
This service module contains functions to generate a list of applications from
random pools of information for testing the ranking system.
"""

import random
import uuid
from datetime import datetime
from typing import List

from backend.schemas.application_schema import (
    Application,
    ApplicationStatus,
    Certification,
    LanguageSkill,
)
from backend.schemas.applicant_schema import Applicant
from backend.schemas.work_experience_schema import WorkExperience
from backend.schemas.education_history_schema import EducationHistory

# NOTE: The _calculate_total_experience function is assumed to be
# correctly implemented in resume_parsing_service.
from backend.services.resume_parsing_service import _calculate_total_experience

# --- English Resume Data Pools ---
EN_FIRST_NAMES = [
    "James",
    "Michael",
    "John",
    "Robert",
    "David",
    "William",
    "Richard",
    "Joseph",
    "Thomas",
    "Charles",
    "Christopher",
    "Daniel",
    "Matthew",
    "Anthony",
    "Mark",
    "Steven",
    "Donald",
    "Andrew",
    "Joshua",
    "Paul",
    "Kevin",
    "Brian",
    "Timothy",
    "Ryan",
    "Jacob",
    "Nicholas",
    "Jonathan",
    "Stephen",
    "Larry",
    "Justin",
    "Benjamin",
    "Scott",
    "Brandon",
    "Samuel",
    "Alexander",
    "Patrick",
    "Frank",
    "Jack",
    "Raymond",
    "Dennis",
    "Tyler",
    "Aaron",
    "Jerry",
    "Jose",
    "Adam",
    "Nathan",
    "Henry",
    "Zachary",
    "Douglas",
    "Peter",
    "Noah",
    "Kyle",
    "Ethan",
    "Christian",
    "Jeremy",
    "Keith",
    "Austin",
    "Sean",
    "Mary",
    "Patricia",
    "Jennifer",
    "Linda",
    "Elizabeth",
    "Barbara",
    "Susan",
    "Jessica",
    "Sarah",
    "Karen",
    "Lisa",
    "Nancy",
    "Betty",
    "Helen",
    "Sandra",
    "Carol",
    "Amanda",
    "Melissa",
    "Deborah",
    "Stephanie",
    "Rebecca",
    "Sharon",
    "Laura",
    "Cynthia",
    "Kathleen",
    "Angela",
    "Brenda",
    "Pamela",
    "Samantha",
    "Anna",
    "Katherine",
    "Christine",
]

EN_LAST_NAMES = [
    "Smith",
    "Jones",
    "Williams",
    "Brown",
    "Davis",
    "Miller",
    "Wilson",
    "Moore",
    "Taylor",
    "Anderson",
    "Thomas",
    "Jackson",
    "White",
    "Harris",
    "Martin",
    "Thompson",
    "Garcia",
    "Martinez",
    "Robinson",
    "Clark",
    "Rodriguez",
    "Lewis",
    "Lee",
    "Walker",
    "Hall",
    "Allen",
    "Young",
    "Hernandez",
    "King",
    "Wright",
    "Lopez",
    "Hill",
    "Scott",
    "Green",
    "Adams",
    "Baker",
    "Gonzalez",
    "Nelson",
    "Carter",
    "Mitchell",
    "Perez",
    "Roberts",
    "Turner",
    "Phillips",
    "Campbell",
    "Parker",
    "Evans",
    "Edwards",
    "Collins",
    "Stewart",
    "Sanchez",
    "Morris",
    "Rogers",
    "Reed",
    "Cook",
    "Morgan",
    "Bell",
    "Murphy",
    "Bailey",
    "Rivera",
    "Cooper",
    "Richardson",
    "Cox",
    "Howard",
    "Ward",
    "Torres",
    "Peterson",
    "Gray",
    "Ramirez",
    "James",
    "Watson",
    "Brooks",
    "Kelly",
    "Sanders",
    "Price",
    "Bennett",
    "Wood",
    "Hughes",
    "Patel",
    "Russell",
]

EN_EMAILS = ["example", "mail", "user", "test", "account", "profile", "contact"]

EN_SKILLS = [
    "Python",
    "JavaScript",
    "SQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "React",
    "Node.js",
    "Django",
    "Flask",
    "C++",
    "Java",
    "CI/CD",
    "Machine Learning",
    "Natural Language Processing (NLP)",
    "Data Science",
    "Big Data",
    "Cybersecurity",
    "DevOps",
    "Cloud Computing",
    "Blockchain",
    "Agile Methodologies",
    "Scrum",
    "Git",
    "REST APIs",
    "TypeScript",
    "HTML5",
    "CSS3",
    "Angular",
    "Vue.js",
    "MongoDB",
    "PostgreSQL",
    "Data Warehousing",
    "ETL",
    "Tableau",
    "Power BI",
    "R",
    "Go",
    "Ruby",
    "C#",
    "Unity",
    "Unreal Engine",
    "Mobile Development (iOS/Android)",
    "UI/UX Design",
    "Figma",
    "Jira",
    "Linux",
    "Shell Scripting",
    "Terraform",
    "Ansible",
    "Kubeflow",
    "Microservices",
    "SQLAlchemy",
    "Celery",
]

EN_JOB_TITLES = [
    "Software Engineer",
    "Data Scientist",
    "DevOps Engineer",
    "Product Manager",
    "Full Stack Developer",
    "Backend Developer",
    "Frontend Developer",
    "AI Engineer",
    "Machine Learning Engineer",
    "Cloud Architect",
    "Cybersecurity Analyst",
    "Data Engineer",
    "Systems Analyst",
    "IT Project Manager",
    "UX/UI Designer",
    "Web Developer",
    "Database Administrator",
    "Network Engineer",
    "QA Analyst",
    "Mobile App Developer",
    "Game Developer",
    "Site Reliability Engineer (SRE)",
    "Technical Lead",
    "Software Architect",
]

EN_COMPANIES = [
    "TechCorp",
    "Innovate Inc.",
    "Global Solutions",
    "Future Systems",
    "Nexus Group",
    "Dynamic Innovations",
    "Pinnacle Technologies",
    "Quantum Leap",
    "Visionary Solutions",
    "Apex Global",
    "Synergy Systems",
    "CoreLogic",
    "DataGenius",
    "CyberSafe",
    "Infinia Labs",
    "TechBridge",
    "AlphaSoft",
    "CloudSphere",
    "DigitalForge",
    "Veridian Dynamics",
]

EN_DEGREES = [
    "Bachelor of Science",
    "Master of Science",
    "Ph.D.",
    "Bachelor of Arts",
    "Master of Arts",
    "Associate's Degree",
    "Master of Engineering",
    "Bachelor of Engineering",
    "Doctor of Philosophy",
]

EN_INSTITUTIONS = [
    "State University",
    "City College",
    "Northwestern University",
    "Massachusetts Institute of Technology (MIT)",
    "Stanford University",
    "University of California, Berkeley",
    "Harvard University",
    "Carnegie Mellon University",
    "University of Oxford",
    "University of Cambridge",
    "Imperial College London",
    "Columbia University",
    "University of Toronto",
    "National University of Singapore (NUS)",
    "ETH Zürich",
    "Peking University",
]

EN_CERTIFICATIONS = [
    "Project Management Professional (PMP)",
    "AWS Certified Developer",
    "Azure Fundamentals",
    "Certified Kubernetes Administrator (CKA)",
    "CompTIA Security+",
    "Google IT Support Professional Certificate",
    "Certified Information Systems Security Professional (CISSP)",
    "Microsoft Certified: Azure Administrator Associate",
    "Cisco Certified Network Associate (CCNA)",
    "Certified Ethical Hacker (CEH)",
]

EN_LANGUAGES = [
    {"name": "English", "level": "Native"},
    {"name": "Spanish", "level": "Intermediate"},
    {"name": "German", "level": "Beginner"},
    {"name": "French", "level": "Fluent"},
    {"name": "Mandarin", "level": "Basic"},
    {"name": "Russian", "level": "Intermediate"},
]


# --- Turkish Resume Data Pools ---
TR_FIRST_NAMES = [
    "Ahmet",
    "Mehmet",
    "Ayşe",
    "Fatma",
    "Can",
    "Deniz",
    "Ebru",
    "Emre",
    "Yusuf",
    "Mustafa",
    "Ali",
    "Hasan",
    "Zeynep",
    "Elif",
    "Murat",
    "Burak",
    "Selin",
    "Gizem",
    "Cem",
    "Berk",
    "Aslı",
    "İrem",
    "Kaan",
    "Kerem",
    "Alper",
    "Dilara",
    "Furkan",
    "Gökhan",
    "Özlem",
    "Pınar",
    "Umut",
    "Volkan",
    "Yağmur",
    "Efe",
    "Tuğçe",
    "İsmail",
    "Sena",
    "Merve",
    "Ege",
    "Batu",
]

TR_LAST_NAMES = [
    "Yılmaz",
    "Kaya",
    "Demir",
    "Çelik",
    "Şahin",
    "Öztürk",
    "Aslan",
    "Kılıç",
    "Arslan",
    "Aydın",
    "Şen",
    "Akyüz",
    "Aksoy",
    "Yıldız",
    "Güneş",
    "Kocaman",
    "Karaca",
    "Sarı",
    "Demirel",
    "Koç",
    "Özdemir",
    "Yıldırım",
    "Tekin",
    "Can",
    "Erdoğan",
    "Uçar",
    "Bulut",
    "Doğan",
    "Korkmaz",
    "Polat",
]

TR_EMAILS = ["ornek", "eposta", "kullanici", "deneme", "hesap", "iletisim"]

TR_SKILLS = [
    "Python",
    "Java",
    "SQL",
    "PostgreSQL",
    "React",
    "Angular",
    "Linux",
    "Bulut Bilişim",
    "Siber Güvenlik",
    "Yapay Zeka (AI)",
    "Makine Öğrenimi (ML)",
    "Veri Analizi",
    "Big Data",
    "Git",
    "RESTful API",
    "Docker",
    "Kubernetes",
    "DevOps",
    "Agile Metodolojileri",
    "Scrum",
    "JavaScript",
    "HTML5",
    "CSS3",
    "C#",
    ".NET",
    "PostgreSQL",
    "MongoDB",
    "ETL",
    "Tableau",
    "Veri Ambarı",
    "UX/UI Tasarımı",
    "Django",
    "Flask",
    "Microservices",
    "SQLAlchemy",
    "Celery",
    "AWS",
]

TR_JOB_TITLES = [
    "Yazılım Mühendisi",
    "Veri Bilimcisi",
    "DevOps Mühendisi",
    "Ürün Yöneticisi",
    "Tam Yığın Geliştirici",
    "Ön Yüz Geliştiricisi",
    "Arka Yüz Geliştiricisi",
    "Yapay Zeka Mühendisi",
    "Bulut Mimarı",
    "Siber Güvenlik Uzmanı",
    "Veri Mühendisi",
    "BT Proje Yöneticisi",
    "Sistem Analisti",
    "Mobil Geliştirici",
]

TR_COMPANIES = [
    "Teknoloji A.Ş.",
    "Gelecek Sistemler",
    "Bilişim Çözümleri",
    "Yıldız Yazılım",
    "Yenilikçi Teknoloji",
    "Bilge Yazılım",
    "Anka Teknoloji",
    "Sistem Mühendislik",
    "Penta Yazılım",
    "Öncü Çözümler",
]

TR_DEGREES = [
    "Lisans Derecesi",
    "Yüksek Lisans",
    "Doktora",
    "Ön Lisans Derecesi",
    "Mühendislik Lisansı",
]

TR_INSTITUTIONS = [
    "Orta Doğu Teknik Üniversitesi (ODTÜ)",
    "Boğaziçi Üniversitesi",
    "İstanbul Teknik Üniversitesi (İTÜ)",
    "Hacettepe Üniversitesi",
    "Bilkent Üniversitesi",
    "Koç Üniversitesi",
    "Sabancı Üniversitesi",
    "Ankara Üniversitesi",
    "Gazi Üniversitesi",
    "İstanbul Üniversitesi",
    "Yıldız Teknik Üniversitesi",
]

TR_CERTIFICATIONS = [
    "PMP Sertifikası",
    "CEH Sertifikası",
    "Siber Güvenlik Uzmanlığı Sertifikası",
    "Yapay Zeka Uzmanlığı Sertifikası",
    "Python Sertifikası",
    "AWS Çözüm Mimarı Sertifikası",
]

TR_LANGUAGES = [
    {"name": "Türkçe", "level": "Ana Dil"},
    {"name": "İngilizce", "level": "İleri Düzey"},
    {"name": "Almanca", "level": "Temel"},
    {"name": "Fransızca", "level": "Orta"},
]


def generate_work_history(
    application_id: uuid.UUID, is_turkish: bool = False
) -> List[WorkExperience]:
    """Generates a list of random work experiences."""
    history = []
    num_jobs = random.randint(1, 4)
    job_titles = TR_JOB_TITLES if is_turkish else EN_JOB_TITLES
    companies = TR_COMPANIES if is_turkish else EN_COMPANIES
    current_year = datetime.now().year

    end_year = current_year
    for _ in range(num_jobs):
        start_year = end_year - random.randint(1, 5)
        start_date = f"01/{start_year}"
        end_date = "present" if _ == 0 and random.random() > 0.5 else f"01/{end_year}"

        history.append(
            WorkExperience(
                id=uuid.uuid4(),
                application_id=application_id,
                job_title=random.choice(job_titles),
                company=random.choice(companies),
                start_date=start_date,
                end_date=end_date,
                description=None,
            )
        )
        end_year = start_year
    return history


def generate_education_history(
    application_id: uuid.UUID, is_turkish: bool = False
) -> List[EducationHistory]:
    """Generates a list of random education entries."""
    degrees = TR_DEGREES if is_turkish else EN_DEGREES
    institutions = TR_INSTITUTIONS if is_turkish else EN_INSTITUTIONS

    return [
        EducationHistory(
            id=uuid.uuid4(),
            application_id=application_id,
            degree=random.choice(degrees),
            institution=random.choice(institutions),
            start_date=f"09/{random.randint(1995, 2020)}",
            end_date=f"06/{random.randint(2021, 2025)}",
            location=None,
        )
    ]


def generate_certifications(is_turkish: bool = False) -> List[Certification]:
    """Generates a list of random certifications."""
    certs = TR_CERTIFICATIONS if is_turkish else EN_CERTIFICATIONS
    return [
        Certification(
            name=random.choice(certs),
            year_issued=str(random.randint(2015, 2025)),
            issuing_organization=None,
        )
        for _ in range(random.randint(0, 3))
    ]


def generate_parsed_skills(is_turkish: bool = False) -> List[str]:
    """Generates a list of random skills."""
    skills = TR_SKILLS if is_turkish else EN_SKILLS
    num_skills = random.randint(5, 12)
    return random.sample(skills, num_skills)


def generate_languages(is_turkish: bool = False) -> List[LanguageSkill]:
    """Generates a list of random languages."""
    return [
        LanguageSkill(
            name=lang["name"],
            level=lang["level"],
        )
        for lang in (TR_LANGUAGES if is_turkish else EN_LANGUAGES)
        if random.random() > 0.2
    ]


def generate_random_application(
    is_turkish: bool = False,
) -> tuple[Applicant, Application]:
    """
    Generates a full Applicant and Application pair with random data.
    The output mimics the structure of the LLM parser's output.
    """
    if is_turkish:
        first_names = TR_FIRST_NAMES
        last_names = TR_LAST_NAMES
        email_domains = TR_EMAILS
        resume_lang = "tr"
    else:
        first_names = EN_FIRST_NAMES
        last_names = EN_LAST_NAMES
        email_domains = EN_EMAILS
        resume_lang = "en"

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    applicant_id = uuid.uuid4()
    application_id = uuid.uuid4()
    current_time = datetime.now()

    work_history = generate_work_history(application_id, is_turkish)
    education_history = generate_education_history(application_id, is_turkish)
    parsed_skills = generate_parsed_skills(is_turkish)
    certifications = generate_certifications(is_turkish)
    languages = generate_languages(is_turkish)

    email_local_part = (
        f"{first_name.lower()}{last_name.lower()}" f"{random.randint(1, 99)}"
    )
    email_domain = random.choice(email_domains)
    email_tld = random.choice(["com", "org", "net"])

    applicant = Applicant(
        applicant_id=applicant_id,
        first_name=first_name,
        last_name=last_name,
        email=f"{email_local_part}@{email_domain}.{email_tld}",
        phone_number=(
            f"+90{''.join(random.choices('0123456789', k=10))}" if is_turkish else None
        ),
        linkedin_profile_url=f"https://linkedin.com/in/{first_name.lower()}{last_name.lower()}",
        github_profile_url=(
            f"https://github.com/{first_name.lower()}-{last_name.lower()}"
            if random.random() > 0.5
            else None
        ),
    )

    total_years_experience = _calculate_total_experience(work_history)

    # Build the parsed_resume_data string by concatenating all relevant fields
    parsed_data_parts = []
    parsed_data_parts.append(f"Resume Language: {resume_lang}")
    parsed_data_parts.append(f"Total Years of Experience: {total_years_experience}")
    parsed_data_parts.append("Work History:")
    for job in work_history:
        parsed_data_parts.append(
            f"- {job.job_title} at {job.company} ({job.start_date} to {job.end_date})"
        )
    parsed_data_parts.append("Education History:")
    for edu in education_history:
        parsed_data_parts.append(
            f"- {edu.degree} from {edu.institution} ({edu.start_date} to {edu.end_date})"
        )
    parsed_data_parts.append("Skills:")
    parsed_data_parts.append(", ".join(parsed_skills))
    parsed_data_parts.append("Certifications:")
    for cert in certifications:
        parsed_data_parts.append(f"- {cert.name} ({cert.year_issued})")
    parsed_data_parts.append("Languages:")
    parsed_data_parts.append(
        ", ".join([f"{lang.name} ({lang.level})" for lang in languages])
    )

    parsed_resume_data = "\n".join(parsed_data_parts)

    application = Application(
        application_id=application_id,
        applicant_id=applicant_id,
        resume_file_path=f"http://example.com/resumes/{application_id}.pdf",
        resume_language=resume_lang,
        total_years_experience=total_years_experience,
        work_history=work_history,
        education_history=education_history,
        parsed_skills=parsed_skills,
        certifications=certifications,
        languages=languages,
        parsed_resume_data=parsed_resume_data,
        status=ApplicationStatus.RECEIVED,
        application_date=current_time,
    )

    return applicant, application


def generate_test_applications(
    count: int, english_ratio: float = 0.5
) -> List[Application]:
    """
    Generates a specified number of test applications, mixing English and Turkish.

    Args:
        count (int): The total number of applications to generate.
        english_ratio (float): The proportion of applications to generate in English.

    Returns:
        A list of generated Application objects.
    """
    applications = []
    num_english = int(count * english_ratio)

    for _ in range(num_english):
        _, app = generate_random_application(is_turkish=False)
        applications.append(app)

    for _ in range(count - num_english):
        _, app = generate_random_application(is_turkish=True)
        applications.append(app)

    random.shuffle(applications)
    return applications


# Example usage
if __name__ == "__main__":
    test_apps = generate_test_applications(10)
    for i, generated_app in enumerate(test_apps):
        print(f"--- Generated Application {i+1} ({generated_app.resume_language}) ---")
        print(generated_app.model_dump_json(indent=2))
        print("\n")
