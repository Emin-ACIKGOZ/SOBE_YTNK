// lib/api/jobs.ts - Jobs API
import apiClient from './base';
import { AxiosResponse } from 'axios';

// Work Experience interface - backend'den ne döneceği bilinmiyor
interface WorkExperience extends Record<string, any> { }

// Education History interface - backend'den ne döneceği bilinmiyor
interface EducationHistory extends Record<string, any> { }

// Ranking Response interface
interface RankingResponse {
    resume_language: string;
    total_years_experience: number;
    parsed_skills: string[];
    certifications: string[];
    languages: string[];
    parsed_resume_data: string;
    status: "RECEIVED" | "PROCESSING" | "COMPLETED" | "FAILED";
    ranking_score: number;
    application_id: string;
    applicant_id: string;
    job_id: string;
    application_date: string;
    resume_file_path: string;
    work_experience: WorkExperience[];
    education_history: EducationHistory[];
}

// Job API functions
export const ranking = (jobId: string, file: File): Promise<AxiosResponse<RankingResponse>> => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/ranking/process/${jobId}`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};


export const getRankings = (jobId: string): Promise<AxiosResponse<RankingResponse[]>> => {
    return apiClient.get(`/ranking/${jobId}`);
}

export const getResumeRankings = (applicationId: string): Promise<AxiosResponse<string>> => {
    return apiClient.get(`/ranking/resume/${applicationId}`);
}


// Export types for use in other components
export type { RankingResponse, WorkExperience, EducationHistory };