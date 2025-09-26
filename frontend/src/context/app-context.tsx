"use client";

import type { ReactNode } from "react";
import { createContext, useState, useCallback, useMemo, useEffect } from "react";
import { getJobs, createJob, JobPosting, JobCreatePayload } from "@/lib/api/jobs";
import { getApplications, createApplication, Application, ApplicationCreate } from "@/lib/api/applications";
import { Applicant, getApplicants } from "@/lib/api/applicants"; // 💡 NEW: Import Applicant API functions and type

// This context provides a global state for job postings, applications, and applicants.
interface AppContextType {
  jobPostings: JobPosting[];
  applications: Application[];
  applicants: Applicant[]; // 💡 NEW: Add applicant data
  // Function to add a new job posting via API.
  addJobPosting: (job: JobCreatePayload) => Promise<JobPosting | undefined>;
  // Function to add a new application via API.
  addApplication: (application: ApplicationCreate) => Promise<Application | undefined>;
  // Function to retrieve a single job posting by its ID.
  getJobById: (id: string) => JobPosting | undefined;
  // Function to retrieve applications for a specific job.
  getApplicationsForJob: (jobId: string) => Application[];
  // 💡 NEW: Function to retrieve a single applicant by their ID.
  getApplicantById: (id: string) => Applicant | undefined;
}

export const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [applicants, setApplicants] = useState<Applicant[]>([]); // 💡 NEW: Initialize applicant state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetches initial data from the backend when the component mounts.
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // 💡 UPDATED: Fetch jobs, applications, and applicants concurrently.
        const [jobsResponse, applicationsResponse, applicantsResponse] = await Promise.all([
          getJobs(),
          getApplications(),
          getApplicants(), // Fetch all applicants
        ]);

        setJobPostings(jobsResponse.data);
        setApplications(applicationsResponse.data);
        setApplicants(applicantsResponse.data); // Update applicant state
        setError(null);
      } catch (err) {
        console.error("Failed to fetch initial data:", err);
        setError("Veri alınırken bir hata oluştu."); // An error occurred while fetching data.
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Adds a new job posting to the backend and updates the state.
  const addJobPosting = useCallback(async (job: JobCreatePayload) => {
    try {
      const response = await createJob(job);
      const newJob = response.data;
      setJobPostings((prev) => [newJob, ...prev]);
      return newJob;
    } catch (err) {
      console.error("Failed to create job posting:", err);
      return undefined;
    }
  }, []);

  // Adds a new application to the backend and updates the state.
  const addApplication = useCallback(async (application: ApplicationCreate) => {
    try {
      const response = await createApplication(application);
      const newApplication = response.data;
      setApplications((prev) => [...prev, newApplication]);
      return newApplication;
    } catch (err) {
      console.error("Failed to create application:", err);
      return undefined;
    }
  }, []);

  // Retrieves a job posting by its ID from the current state.
  const getJobById = useCallback((id: string) => {
    return jobPostings.find((job) => job.job_id === id);
  }, [jobPostings]);

  // Retrieves all applications for a specific job ID.
  const getApplicationsForJob = useCallback((jobId: string) => {
    return applications
      .filter((app) => app.job_id === jobId)
      .sort((a, b) => (b.ranking_score || 0) - (a.ranking_score || 0));
  }, [applications]);

  // Retrieves an applicant by their ID from the current state.
  const getApplicantById = useCallback((id: string) => {
    return applicants.find((applicant) => applicant.applicant_id === id);
  }, [applicants]);

  const value = useMemo(
    () => ({
      jobPostings,
      applications,
      applicants, // 💡 NEW: Expose applicants
      addJobPosting,
      addApplication,
      getJobById,
      getApplicationsForJob,
      getApplicantById, // 💡 NEW: Expose getter function
    }),
    [
      jobPostings,
      applications,
      applicants, // 💡 NEW: Dependency
      addJobPosting,
      addApplication,
      getJobById,
      getApplicationsForJob,
      getApplicantById, // 💡 NEW: Dependency
    ]
  );

  if (loading) {
    return <div>Veriler yükleniyor...</div>; // Data is loading...
  }

  if (error) {
    return <div>Hata: {error}</div>; // Error: {error}
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
