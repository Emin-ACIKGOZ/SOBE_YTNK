'use client';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { useApp } from '@/hooks/use-app';
import { PlusCircle, Users, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getJobs, deleteJob, JobPosting } from '@/lib/api/jobs';
import Swal from 'sweetalert2';

export default function JobsPage() {
  const { getApplicationsForJob } = useApp();
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);

  useEffect(() => {
    getJobs()
      .then((response) => {
        setJobPostings(response.data);
      })
      .catch((error) => {
        console.error('Error fetching jobs:', error);
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

        setJobPostings(jobPostings.filter((job) => job.job_id !== jobId));

        Swal.fire('Silindi!', 'İş ilanı başarıyla silindi.', 'success');
      } catch (error) {
        console.error('Error deleting job:', error);
        Swal.fire('Hata!', 'İş ilanı silinirken bir hata oluştu.', 'error');
      }
    }
  };

  return (
    <div className="container mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-headline text-3xl font-bold">İş İlanları</h1>
          <p className="text-muted-foreground">
            Açık pozisyonlarınızı ve başvuruları yönetin.
          </p>
        </div>
        <Link href="/jobs/new">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            Yeni İş İlanı Oluştur
          </Button>
        </Link>
      </div>

      {jobPostings.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed py-20 text-center">
          <h2 className="text-xl font-semibold">İş İlanı Yok</h2>
          <p className="mt-2 text-muted-foreground">
            İlk iş ilanınızı oluşturun
          </p>
          <Link href="/jobs/new" className="mt-4 inline-block">
            <Button>Yeni İş İlanı Oluştur</Button>
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {jobPostings.map((job) => {
            const candidateCount = getApplicationsForJob(job.job_id).length;
            return (
              <Card
                key={job.job_id}
                className="flex flex-col transition-shadow hover:shadow-lg"
              >
                <CardHeader className="relative">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute right-2 top-2 h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                    onClick={() => handleDeleteJob(job.job_id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <CardTitle className="pr-10">{job.title}</CardTitle>
                  <CardDescription>
                    {new Date(job.posted_at ?? '').toLocaleDateString('tr-TR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}{' '}
                    tarihinde paylaşıldı
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-grow">
                  <p className="line-clamp-3 text-sm text-muted-foreground">
                    {job.description}
                  </p>
                  <div className="mt-2 text-xs text-muted-foreground">
                    <p>
                      <strong>Şirket:</strong> {job.company_name}
                    </p>
                    <p>
                      <strong>Lokasyon:</strong> {job.location}
                    </p>
                    <p>
                      <strong>Seviye:</strong> {job.seniority_level}
                    </p>
                    <p>
                      <strong>Çalışma Şekli:</strong> {job.employment_type}
                    </p>
                  </div>
                </CardContent>
                <CardFooter className="flex items-center justify-between">
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
