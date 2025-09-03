export interface JobPosting {
  id: string;
  title: string;
  description: string;
  requirements: string;
  createdAt: Date;
}

export interface Candidate {
  id: string;
  jobId: string;
  fileName: string;
  cvDataUri: string;
  matchScore: number;
  reasoning: string;
  createdAt: Date;
}
