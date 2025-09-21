"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useApp } from "@/hooks/use-app";
import { PlusCircle, Users, Trash2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getJobs, deleteJob } from "@/lib/api";
import Swal from 'sweetalert2';

// Job tipini tanımla
interface Job {
  job_id: string;
  title: string;
  company_name: string;
  location: string;
  seniority_level: "INTERNSHIP" | "JUNIOR" | "MID" | "SENIOR";
  employment_type: "FULL_TIME" | "PART_TIME" | "CONTRACT";
  description: string;
  responsibilities: string[];
  qualifications: string[];
  required_skills: string[];
  salary: string;
  posted_at: string;
  is_active: boolean;
}

export default function JobsPage() {
  const { getCandidatesForJob } = useApp(); // useApp'den getCandidatesForJob'ı al
  const [jobPostings, setJobPostings] = useState<Job[]>([]); // Job array tipi belirt

  useEffect(() => {
    getJobs().then((response) => {
      // JobsListResponse'u unknown üzerinden Job[] tipine dönüştür
      setJobPostings(response.data as unknown as Job[]);
    }).catch((error) => {
      console.error("Error fetching jobs:", error);
    });
  }, []);

  const handleDeleteJob = async (jobId: string) => {
    const result = await Swal.fire({
      title: 'Emin misiniz?',
      text: 'Bu iş ilanını silmek istediğinizden emin misiniz?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Evet, sil',
      cancelButtonText: 'Hayır, iptal et',
      reverseButtons: true,
    });

    if (result.isConfirmed) {
      try {
        await deleteJob(jobId);

        setJobPostings(jobPostings.filter(job => job.job_id !== jobId));

        Swal.fire('Silindi!', 'İş ilanı başarıyla silindi.', 'success');
      } catch (error) {
        console.error("Error deleting job:", error);
        Swal.fire('Hata!', 'İş ilanı silinirken bir hata oluştu.', 'error');
      }
    }
  };


  return (
    <div className="container mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold font-headline">İş İlanları</h1>
          <p className="text-muted-foreground">Açık pozisyonlarınızı ve başvuruları yönetin.</p>
        </div>
        <Link href="/jobs/new">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            Yeni İş İlanı Oluştur
          </Button>
        </Link>
      </div>

      {jobPostings.length === 0 ? (
        <div className="text-center py-20 border-2 border-dashed rounded-lg">
          <h2 className="text-xl font-semibold">İş İlanı Yok</h2>
          <p className="text-muted-foreground mt-2">İlk iş ilanınızı oluşturun</p>
          <Link href="/jobs/new" className="mt-4 inline-block">
            <Button>Yeni İş İlanı Oluştur</Button>
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {jobPostings.map((job) => {
            const candidateCount = getCandidatesForJob(job.job_id).length;
            return (
              <Card key={job.job_id} className="flex flex-col transition-shadow hover:shadow-lg">
                <CardHeader className="relative">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute top-2 right-2 h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                    onClick={() => handleDeleteJob(job.job_id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <CardTitle className="pr-10">{job.title}</CardTitle>
                  <CardDescription>
                    {new Date(job.posted_at).toLocaleDateString("tr-TR", {
                      year: "numeric",
                      month: "long",
                      day: "numeric"
                    })} tarihinde paylaşıldı
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-grow">
                  <p className="text-sm text-muted-foreground line-clamp-3">{job.description}</p>
                  <div className="mt-2 text-xs text-muted-foreground">
                    <p><strong>Şirket:</strong> {job.company_name}</p>
                    <p><strong>Lokasyon:</strong> {job.location}</p>
                    <p><strong>Seviye:</strong> {job.seniority_level}</p>
                    <p><strong>Çalışma Şekli:</strong> {job.employment_type}</p>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between items-center">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Users className="mr-2 h-4 w-4" />
                    {candidateCount} başvuru
                  </div>
                  <Link href={`/jobs/${job.job_id}`}>
                    <Button variant="secondary">Detay Görüntüle</Button>
                  </Link>
                </CardFooter>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}