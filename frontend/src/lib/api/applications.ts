import apiClient from './base';
import { AxiosResponse } from 'axios';

// ----------------------------------------------------
// Frontend Schemas for Backend Data Models
// These interfaces match the Pydantic schemas on the backend
// to ensure type safety.
// ----------------------------------------------------

export interface WorkExperience {
    job_title: string;
    company_name: string;
    start_date: string;
    end_date: string | null;
    is_current: boolean;
    description: string;
}

export interface EducationHistory {
    institution_name: string;
    degree: string;
    field_of_study: string;
    start_date: string;
    end_date: string | null;
}

export interface Certification {
    name: string;
    issuing_organization: string;
    issue_date: string;
}

export interface Language {
    language: string;
    proficiency: 'beginner' | 'intermediate' | 'advanced' | 'fluent' | 'native';
}

export interface Application {
    application_id: string;
    job_id: string;
    applicant_id: string;
    application_date: string;
    status: 'RECEIVED' | 'IN_REVIEW' | 'REJECTED' | 'ACCEPTED';
    resume_file_path: string | null;
    resume_language: string | null;
    total_years_experience: number | null;
    parsed_skills: string[] | null;
    certifications: Certification[] | null;
    languages: Language[] | null;
    parsed_resume_data: string | null;
    ranking_score: number | null;
    // Relationships
    work_experience: WorkExperience[] | null;
    education_history: EducationHistory[] | null;
}

// NOTE: This interface is for creating a new application, without the backend-generated fields.
export interface ApplicationCreate extends Omit<Application, 'application_id' | 'application_date' | 'status' | 'ranking_score'> {
    status?: 'RECEIVED' | 'IN_REVIEW' | 'REJECTED' | 'ACCEPTED';
}

// ----------------------------------------------------
// API Functions
// ----------------------------------------------------

/**
 * Fetches all applications from the backend.
 * NOTE: This function assumes the backend has a GET /applications endpoint
 * that returns a list of all applications.
 */
export const getApplications = (): Promise<AxiosResponse<Application[]>> => {
    return apiClient.get('/applications');
};

/**
 * Fetches a single application by its ID.
 * @param id The UUID of the application.
 */
export const getApplicationById = (id: string): Promise<AxiosResponse<Application>> => {
    return apiClient.get(`/applications/${id}`);
};

/**
 * Fetches all applications for a specific applicant.
 * @param applicantId The UUID of the applicant.
 */
export const getApplicationsByApplicant = (applicantId: string): Promise<AxiosResponse<Application[]>> => {
    return apiClient.get(`/applications/by-applicant/${applicantId}`);
};

/**
 * Fetches all applications for a specific job.
 * @param jobId The UUID of the job posting.
 */
export const getApplicationsForJob = (jobId: string): Promise<AxiosResponse<Application[]>> => {
    return apiClient.get(`/applications/by-job/${jobId}`);
};

/**
 * Creates a new application on the backend.
 * @param application The new application data.
 */
export const createApplication = (application: ApplicationCreate): Promise<AxiosResponse<Application>> => {
    return apiClient.post('/applications', application);
};

/**
 * Updates the status of an application.
 * @param applicationId The UUID of the application to update.
 * @param newStatus The new status to set for the application.
 */
export const updateApplicationStatus = (applicationId: string, newStatus: Application['status']): Promise<AxiosResponse<Application>> => {
    // The key should be `new_status` to match the backend function's parameter name.
    return apiClient.put(`/applications/${applicationId}/status`, { new_status: newStatus });
};
