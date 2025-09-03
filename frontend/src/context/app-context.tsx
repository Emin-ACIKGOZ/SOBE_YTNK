"use client";

import type { ReactNode } from "react";
import { createContext, useState, useCallback, useMemo } from "react";
import type { JobPosting, Candidate } from "@/lib/types";

// mock data
const initialJobs: JobPosting[] = [
  {
    id: "1",
    title: "Kıdemli Frontend Geliştirici",
    description: "Ekibimize katılacak Kıdemli Frontend Geliştirici arıyoruz. İdeal adayın React, Next.js ve TypeScript konusunda deneyimli olması bekleniyor.",
    requirements: "Frontend geliştirmede 5+ yıl deneyim. React, Next.js ve TypeScript konusunda uzmanlık. Web performansı ve erişilebilirlik hakkında güçlü bilgi.",
    createdAt: new Date("2023-10-26T10:00:00Z"),
  },
  {
    id: "2",
    title: "Ürün Tasarımcısı",
    description: "Güzel ve sezgisel kullanıcı deneyimleri oluşturmak için tasarım ekibimize katılın. Ürün tasarım yaşam döngüsünün tüm aşamalarında çalışacaksınız.",
    requirements: "Ürün tasarımında 3+ yıl deneyim. Önceki çalışmalardan oluşan güçlü bir portföy. Figma, Sketch veya Adobe XD konusunda yetkinlik.",
    createdAt: new Date("2023-10-25T14:30:00Z"),
  },
];

const initialCandidates: Candidate[] = [];

interface AppContextType {
  jobPostings: JobPosting[];
  candidates: Candidate[];
  addJobPosting: (job: Omit<JobPosting, "id" | "createdAt">) => JobPosting;
  addCandidate: (candidate: Omit<Candidate, "id" | "createdAt">) => Candidate;
  getJobById: (id: string) => JobPosting | undefined;
  getCandidatesForJob: (jobId: string) => Candidate[];
}

export const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [jobPostings, setJobPostings] = useState<JobPosting[]>(initialJobs);
  const [candidates, setCandidates] = useState<Candidate[]>(initialCandidates);

  const addJobPosting = useCallback((job: Omit<JobPosting, "id" | "createdAt">) => {
    const newJob: JobPosting = {
      ...job,
      id: (jobPostings.length + 1).toString(),
      createdAt: new Date(),
    };
    setJobPostings((prev) => [newJob, ...prev]);
    return newJob;
  }, [jobPostings]);

  const addCandidate = useCallback((candidate: Omit<Candidate, "id" | "createdAt">) => {
    const newCandidate: Candidate = {
      ...candidate,
      id: (candidates.length + 1).toString(),
      createdAt: new Date(),
    };
    setCandidates((prev) => [...prev, newCandidate]);
    return newCandidate;
  }, [candidates]);

  const getJobById = useCallback((id: string) => {
    return jobPostings.find((job) => job.id === id);
  }, [jobPostings]);

  const getCandidatesForJob = useCallback((jobId: string) => {
    return candidates
      .filter((c) => c.jobId === jobId)
      .sort((a, b) => b.matchScore - a.matchScore);
  }, [candidates]);

  const value = useMemo(
    () => ({
      jobPostings,
      candidates,
      addJobPosting,
      addCandidate,
      getJobById,
      getCandidatesForJob,
    }),
    [jobPostings, candidates, addJobPosting, addCandidate, getJobById, getCandidatesForJob]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
