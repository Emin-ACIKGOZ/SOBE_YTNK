"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { useApp } from "@/hooks/use-app";
import { useToast } from "@/hooks/use-toast";
import { matchCandidate } from "@/ai/flows/ai-candidate-matching";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Users } from "lucide-react";
import { CvUpload } from "@/components/cv-upload";
import { CandidateCard } from "@/components/candidate-card";

export default function JobDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { getJobById, addCandidate, getCandidatesForJob } = useApp();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const jobId = Array.isArray(params.id) ? params.id[0] : params.id;
  const job = jobId ? getJobById(jobId) : undefined;
  const candidates = jobId ? getCandidatesForJob(jobId) : [];

  const handleFileUpload = async (cvDataUri: string, file: File) => {
    if (!job) return;

    setIsLoading(true);
    try {
      const result = await matchCandidate({
        jobDescription: `${job.title}\n\nDescription:\n${job.description}\n\Gereksinimler:\n${job.requirements}`,
        cvDataUri,
      });

      addCandidate({
        jobId: job.id,
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

  if (!job) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-semibold">İş ilanı bulunamadı</h2>
        <p className="text-muted-foreground mt-2">Bu iş ilanı mevcut değil veya kaldırılmış.</p>
        <Link href="/jobs" className="mt-4 inline-block">
          <Button>Geri dön</Button>
        </Link>
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
              <CardDescription>{job.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <h4 className="font-semibold mb-2">Gereksinimler</h4>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">{job.requirements}</p>
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
