"use client";

import type { ReactNode } from "react";
import { createContext, useState, useCallback, useMemo, useEffect } from "react";
import { getJobs, createJob, JobPosting, JobCreatePayload } from "@/lib/api/jobs";
import { getApplications, createApplication, Application, ApplicationCreate } from "@/lib/api/applications";
import { Applicant, getApplicants } from "@/lib/api/applicants";

interface AppContextType {
  jobPostings: JobPosting[];
  applications: Application[];
  applicants: Applicant[];
  addJobPosting: (job: JobCreatePayload) => Promise<JobPosting | undefined>;
  addApplication: (application: ApplicationCreate) => Promise<Application | undefined>;
  getJobById: (id: string) => JobPosting | undefined;
  getApplicationsForJob: (jobId: string) => Application[];
  getApplicantById: (id: string) => Applicant | undefined;
}

export const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [jobsResponse, applicationsResponse, applicantsResponse] = await Promise.all([
          getJobs(),
          getApplications(),
          getApplicants(),
        ]);

        setJobPostings(jobsResponse.data);
        setApplications(applicationsResponse.data);
        setApplicants(applicantsResponse.data);
        setError(null);
      } catch (err) {
        setError("Veri alınırken bir hata oluştu.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const addJobPosting = useCallback(async (job: JobCreatePayload) => {
    try {
      const response = await createJob(job);
      const newJob = response.data;
      setJobPostings((prev) => [newJob, ...prev]);
      return newJob;
    } catch (err) {
      return undefined;
    }
  }, []);

  const addApplication = useCallback(async (application: ApplicationCreate) => {
    try {
      const response = await createApplication(application);
      const newApplication = response.data;
      setApplications((prev) => [...prev, newApplication]);
      return newApplication;
    } catch (err) {
      return undefined;
    }
  }, []);

  const getJobById = useCallback((id: string) => {
    return jobPostings.find((job) => job.job_id === id);
  }, [jobPostings]);

  const getApplicationsForJob = useCallback((jobId: string) => {
    return applications
      .filter((app) => app.job_id === jobId)
      .sort((a, b) => (b.ranking_score || 0) - (a.ranking_score || 0));
  }, [applications]);

  const getApplicantById = useCallback((id: string) => {
    return applicants.find((applicant) => applicant.applicant_id === id);
  }, [applicants]);

  const value = useMemo(
    () => ({
      jobPostings,
      applications,
      applicants,
      addJobPosting,
      addApplication,
      getJobById,
      getApplicationsForJob,
      getApplicantById,
    }),
    [
      jobPostings,
      applications,
      applicants,
      addJobPosting,
      addApplication,
      getJobById,
      getApplicationsForJob,
      getApplicantById,
    ]
  );

  if (loading) {
    return <div>Veriler yükleniyor...</div>;
  }

  if (error) {
    return <div>Hata: {error}</div>;
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
