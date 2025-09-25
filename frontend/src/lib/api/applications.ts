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

// Updated the status property to include all possible statuses from the UI.
export interface Application {
    application_id: string;
    job_id: string;
    applicant_id: string;
    application_date: string;
    status: 'RECEIVED' | 'IN_REVIEW' | 'REJECTED' | 'ACCEPTED' | 'SHORTLISTED' | 'INTERVIEW_SCHEDULED' | 'OFFER_EXTENDED' | 'HIRED';
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

// This interface is for creating a new application, without the backend-generated fields.
export interface ApplicationCreate extends Omit<Application, 'application_id' | 'application_date' | 'status' | 'ranking_score'> {
    status?: 'RECEIVED' | 'IN_REVIEW' | 'REJECTED' | 'ACCEPTED' | 'SHORTLISTED' | 'INTERVIEW_SCHEDULED' | 'OFFER_EXTENDED' | 'HIRED';
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
    // FIX: The backend endpoint expects the new status as a query parameter in the URL.
    // This has been updated to match the backend's API signature.
    return apiClient.put(`/applications/${applicationId}/status?new_status=${newStatus}`);
};

// The following functions were commented out because they do not have
// a corresponding endpoint in the provided backend code.

// export const getRankings = (jobId: string): Promise<AxiosResponse<any>> => {
//     return apiClient.get(`/applications/rankings/${jobId}`);
// };

// export const getResumeRankings = (jobId: string): Promise<AxiosResponse<any>> => {
//     return apiClient.get(`/applications/resume-rankings/${jobId}`);
// };

// export const sendResumeForRanking = (jobId: string, file: File): Promise<AxiosResponse<any>> => {
//     const formData = new FormData();
//     formData.append('file', file);
//     return apiClient.post(`/applications/rank/${jobId}`, formData, {
//         headers: {
//             'Content-Type': 'multipart/form-data',
//         },
//     });
// };

// export const getResumeFile = (filePath: string): Promise<AxiosResponse<Blob>> => {
//     return apiClient.get(filePath, { responseType: 'blob' });
// };

/**
 * The backend has endpoints for recalculating ranks. These functions were added
 * to allow you to call those endpoints from the frontend.
 */

/**
 * Recalculates the rank for a single application.
 * @param applicationId The UUID of the application to update.
 */
export const recalculateSingleApplicationRank = (applicationId: string): Promise<AxiosResponse<Application>> => {
    return apiClient.post(`/applications/${applicationId}/recalculate-rank`);
};

/**
 * Recalculates the ranks for all applications under a specific job ID.
 * @param jobId The UUID of the job posting.
 */
export const recalculateApplicationsForJobRank = (jobId: string): Promise<AxiosResponse<Application[]>> => {
    return apiClient.post(`/applications/by-job/${jobId}/recalculate-ranks`);
};
