// lib/api/jobs.ts - Jobs API
import apiClient from './base';
import { AxiosResponse } from 'axios';

// Job Types
export interface JobPosting {
    id?: string;
    title: string;
    company_name: string;
    location: string;
    seniority_level: 'INTERNSHIP' | 'JUNIOR' | 'MID' | 'SENIOR' | 'LEAD';
    employment_type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'TEMPORARY';
    description: string;
    responsibilities: string[];
    qualifications: string[];
    required_skills: string[];
    salary?: string;
    created_at?: string;
    updated_at?: string;
}

export interface JobCreatePayload {
    title: string;
    company_name: string;
    location: string;
    seniority_level: 'INTERNSHIP' | 'JUNIOR' | 'MID' | 'SENIOR' | 'LEAD';
    employment_type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'TEMPORARY';
    description: string;
    responsibilities: string[];
    qualifications: string[];
    required_skills: string[];
    salary?: string;
}

export interface JobsListResponse {
    jobs: JobPosting[];
    total: number;
    page: number;
    per_page: number;
}

// Job API functions
export const createJob = (jobData: JobCreatePayload): Promise<AxiosResponse<JobPosting>> => {
    return apiClient.post('/jobs/', jobData);
};

export const getJobs = (params?: {
    skip?: number;
    limit?: number;
}): Promise<AxiosResponse<JobsListResponse>> => {
    return apiClient.get('/jobs/', { params });
};

export const getJob = (id: string): Promise<AxiosResponse<JobPosting>> => {
    return apiClient.get(`/jobs/${id}`);
};

export const updateJob = (id: string, jobData: Partial<JobCreatePayload>): Promise<AxiosResponse<JobPosting>> => {
    return apiClient.put(`/jobs/${id}`, jobData);
};

export const deleteJob = (id: string): Promise<AxiosResponse<void>> => {
    return apiClient.delete(`/jobs/${id}`);
};

// Job search
export const searchJobs = (query: string, filters?: {
    seniority_level?: string;
    employment_type?: string;
    location?: string;
}): Promise<AxiosResponse<JobsListResponse>> => {
    return apiClient.get('/jobs/search', {
        params: { q: query, ...filters }
    });
};

// Get jobs by company
export const getJobsByCompany = (companyName: string): Promise<AxiosResponse<JobsListResponse>> => {
    return apiClient.get(`/jobs/company/${encodeURIComponent(companyName)}`);
};

// Apply to job (if you have this endpoint)
export const applyToJob = (jobId: string, applicationData: any): Promise<AxiosResponse<any>> => {
    return apiClient.post(`/jobs/${jobId}/apply`, applicationData);
};