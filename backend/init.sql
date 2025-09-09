-- Drop tables and enums in the correct order to avoid foreign key constraint errors
DROP TABLE IF EXISTS work_experiences CASCADE;
DROP TABLE IF EXISTS education_history CASCADE;
DROP TABLE IF EXISTS applications CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS applicants CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS applicationstatus CASCADE;
DROP TYPE IF EXISTS senioritylevel CASCADE;
DROP TYPE IF EXISTS employmenttype CASCADE;
DROP TYPE IF EXISTS userrole CASCADE;

-- Create Enums
CREATE TYPE userrole AS ENUM ('HR', 'APPLICANT');
CREATE TYPE senioritylevel AS ENUM ('INTERNSHIP', 'ENTRY_LEVEL', 'JUNIOR_LEVEL', 'MID_LEVEL', 'SENIOR_LEVEL', 'DIRECTOR', 'EXECUTIVE');
CREATE TYPE employmenttype AS ENUM ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP');
CREATE TYPE applicationstatus AS ENUM ('RECEIVED', 'IN_REVIEW', 'SHORTLISTED', 'REJECTED', 'HIRED');

-- Create the users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role userrole NOT NULL
);

-- Create the applicants table
CREATE TABLE applicants (
    applicant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    phone_number VARCHAR,
    linkedin_profile_url VARCHAR,
    github_profile_url VARCHAR
);

-- Create the jobs table
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR NOT NULL,
    company_name VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    seniority_level senioritylevel NOT NULL,
    employment_type employmenttype NOT NULL,
    description VARCHAR NOT NULL,
    responsibilities VARCHAR[] DEFAULT '{}',
    qualifications VARCHAR[] DEFAULT '{}',
    required_skills VARCHAR[] DEFAULT '{}',
    salary VARCHAR,
    posted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create the applications table
CREATE TABLE applications (
    application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    applicant_id UUID NOT NULL REFERENCES applicants(applicant_id) ON DELETE CASCADE,
    application_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status applicationstatus NOT NULL DEFAULT 'RECEIVED',
    resume_file_path VARCHAR NOT NULL,
    resume_language VARCHAR,
    total_years_experience INTEGER,
    parsed_skills VARCHAR[],
    certifications JSONB,
    languages JSONB,
    parsed_resume_data TEXT,
    ranking_score FLOAT
);

-- Create the work_experiences table
CREATE TABLE work_experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    job_title VARCHAR NOT NULL,
    company VARCHAR NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    description VARCHAR
);

-- Create the education_history table
CREATE TABLE education_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    degree VARCHAR NOT NULL,
    institution VARCHAR NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    location VARCHAR
);
