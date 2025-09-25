// lib/api/jobs.ts - Jobs API
import apiClient from './base';
import { AxiosResponse } from 'axios';

// Job Types
export interface JobPosting {
    job_id: string; // Corrected to match backend model
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
    posted_at?: string; // Corrected to match backend model
    updated_at?: string;
    is_active: boolean; // Added for soft-delete state tracking
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

// NOTE: Since your backend API returns an array, this structure might be slightly off.
// Based on the *provided* code, we'll assume the /jobs/ endpoint returns an array directly,
// but the component code suggests a wrapper object, so we'll keep the wrapper interface.
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
    // The backend is fixed to filter out inactive jobs here.
    return apiClient.get('/jobs/', { params });
};

export const getJob = (id: string): Promise<AxiosResponse<JobPosting>> => {
    return apiClient.get(`/jobs/${id}`);
};

export const updateJob = (id: string, jobData: Partial<JobCreatePayload>): Promise<AxiosResponse<JobPosting>> => {
    return apiClient.put(`/jobs/${id}`, jobData);
};

export const deleteJob = (id: string): Promise<AxiosResponse<void>> => {
    // This calls the backend's soft-delete endpoint.
    return apiClient.delete(`/jobs/${id}`);
};