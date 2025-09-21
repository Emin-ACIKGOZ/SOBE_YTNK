"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useApp } from "@/hooks/use-app";
import { useToast } from "@/hooks/use-toast";
import { matchCandidate } from "@/ai/flows/ai-candidate-matching";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Users, Loader2, MapPin, Building2, Clock, DollarSign } from "lucide-react";
import { CvUpload } from "@/components/cv-upload";
import { CandidateCard } from "@/components/candidate-card";
import { getJob } from "@/lib/api";

// API'den gelen veri yapısına uygun Job interface'i
interface Job {
  job_id: string;
  title: string;
  description: string;
  company_name: string;
  location: string;
  employment_type: string;
  seniority_level: string;
  salary: string | null;
  qualifications: string[];
  required_skills: string[];
  responsibilities: string[];
  is_active: boolean;
  posted_at: string;
}

// Employment type ve seniority level için Türkçe etiketler
const EMPLOYMENT_TYPE_LABELS: Record<string, string> = {
  'FULL_TIME': 'Tam Zamanlı',
  'PART_TIME': 'Yarı Zamanlı',
  'CONTRACT': 'Sözleşmeli',
  'INTERNSHIP': 'Staj',
  'FREELANCE': 'Serbest Çalışan'
};

const SENIORITY_LEVEL_LABELS: Record<string, string> = {
  'INTERNSHIP': 'Staj',
  'JUNIOR': 'Junior',
  'MID': 'Mid-Level',
  'SENIOR': 'Senior',
  'LEAD': 'Lead',
  'MANAGER': 'Manager'
};

export default function JobDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { addCandidate, getCandidatesForJob } = useApp();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [job, setJob] = useState<Job | null>(null);
  const [isJobLoading, setIsJobLoading] = useState(true);
  const [jobError, setJobError] = useState<string | null>(null);

  const jobId = Array.isArray(params.id) ? params.id[0] : params.id;
  const candidates = jobId ? getCandidatesForJob(jobId) : [];

  useEffect(() => {
    if (!jobId) {
      setIsJobLoading(false);
      return;
    }

    const fetchJob = async () => {
      try {
        setIsJobLoading(true);
        setJobError(null);
        const response = await getJob(jobId);
        setJob(response.data as Job);
      } catch (error) {
        console.error("Error fetching job:", error);
        setJobError("İş ilanı yüklenirken bir hata oluştu.");
      } finally {
        setIsJobLoading(false);
      }
    };

    fetchJob();
  }, [jobId]);

  const handleFileUpload = async (cvDataUri: string, file: File) => {
    if (!job) return;

    setIsLoading(true);
    try {
      // İş tanımını daha kapsamlı bir şekilde hazırlayalım
      const fullJobDescription = `
Pozisyon: ${job.title}
Şirket: ${job.company_name}
Lokasyon: ${job.location}
Çalışma Türü: ${EMPLOYMENT_TYPE_LABELS[job.employment_type] || job.employment_type}
Seviye: ${SENIORITY_LEVEL_LABELS[job.seniority_level] || job.seniority_level}

Açıklama:
${job.description}

Sorumluluklar:
${job.responsibilities.join('\n')}

Gerekli Yetenekler:
${job.required_skills.join('\n')}

Nitelikler:
${job.qualifications.join('\n')}
      `.trim();

      const result = await matchCandidate({
        jobDescription: fullJobDescription,
        cvDataUri,
      });

      addCandidate({
        jobId: job.job_id,
        fileName: file.name,
        cvDataUri,
        matchScore: result.matchScore,
        reasoning: result.reasoning,
      });

      toast({
        title: "Aday Eşleşti",
        description: `${file.name} analiz edildi. Eşleşme skoru: ${Math.round(result.matchScore * 100)}%`,
      });
    } catch (error) {
      console.error("AI matching failed:", error);
      toast({
        variant: "destructive",
        title: "Analiz Başarısız",
        description: "CV analiz edilirken bir hata oluştu. Lütfen tekrar deneyin.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  if (isJobLoading) {
    return (
      <div className="container mx-auto">
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">İş ilanı yükleniyor...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (jobError) {
    return (
      <div className="container mx-auto">
        <div className="text-center py-20">
          <h2 className="text-xl font-semibold text-red-600">Hata</h2>
          <p className="text-muted-foreground mt-2">{jobError}</p>
          <Link href="/jobs" className="mt-4 inline-block">
            <Button>İş İlanları</Button>
          </Link>
        </div>
      </div>
    );
  }

  // Job not found
  if (!job) {
    return (
      <div className="container mx-auto">
        <div className="text-center py-20">
          <h2 className="text-xl font-semibold">İş ilanı bulunamadı</h2>
          <p className="text-muted-foreground mt-2">Bu iş ilanı mevcut değil veya kaldırılmış.</p>
          <Link href="/jobs" className="mt-4 inline-block">
            <Button>İş İlanları</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto">
      <Button variant="ghost" size="sm" onClick={() => router.back()} className="mb-4 -ml-4">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Geri dön
      </Button>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="font-headline">{job.title}</CardTitle>
              <CardDescription className="flex items-center gap-2">
                <Building2 className="h-4 w-4" />
                {job.company_name}
              </CardDescription>
              <div className="flex flex-wrap gap-2 pt-2">
                <Badge variant="secondary" className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  {job.location}
                </Badge>
                <Badge variant="outline">
                  {EMPLOYMENT_TYPE_LABELS[job.employment_type] || job.employment_type}
                </Badge>
                <Badge variant="outline">
                  {SENIORITY_LEVEL_LABELS[job.seniority_level] || job.seniority_level}
                </Badge>
                {job.salary && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    <DollarSign className="h-3 w-3" />
                    {job.salary}
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Açıklama</h4>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">{job.description}</p>
              </div>

              {job.responsibilities.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Sorumluluklar</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {job.responsibilities.map((responsibility, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-primary mt-1">•</span>
                        <span>{responsibility}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {job.required_skills.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Gerekli Yetenekler</h4>
                  <div className="flex flex-wrap gap-1">
                    {job.required_skills.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {job.qualifications.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Nitelikler</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    {job.qualifications.map((qualification, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-primary mt-1">•</span>
                        <span>{qualification}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="pt-2 border-t">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>İlan Tarihi: {formatDate(job.posted_at)}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                  <div className={`h-2 w-2 rounded-full ${job.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span>{job.is_active ? 'Aktif' : 'Pasif'}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="font-headline text-xl">CV Yükle</CardTitle>
              <CardDescription>Bu iş ilanına uygun adayın CV'sini yükleyin.</CardDescription>
            </CardHeader>
            <CardContent>
              <CvUpload onFileUpload={handleFileUpload} isLoading={isLoading} />
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          <Card className="min-h-full">
            <CardHeader>
              <CardTitle className="font-headline">Eşleşen Adaylar</CardTitle>
              <CardDescription>Bu pozisyona başvuran adaylar, eşleşme skoruna göre sıralanmıştır.</CardDescription>
            </CardHeader>
            <CardContent>
              {candidates.length > 0 ? (
                <div className="space-y-4">
                  {candidates.map((candidate) => (
                    <CandidateCard key={candidate.id} candidate={candidate} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-16 border-2 border-dashed rounded-lg flex flex-col items-center justify-center h-full">
                  <Users className="mx-auto h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-4 text-lg font-medium">Henüz aday yok</h3>
                  <p className="mt-1 text-sm text-muted-foreground">Burada eşleşen adayları görmek için bir CV yükleyin.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}