"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useApp } from "@/hooks/use-app";
import { PlusCircle, Users } from "lucide-react";
import Link from "next/link";

export default function JobsPage() {
  const { jobPostings, getCandidatesForJob } = useApp();

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
            const candidateCount = getCandidatesForJob(job.id).length;
            return (
              <Card key={job.id} className="flex flex-col transition-shadow hover:shadow-lg">
                <CardHeader>
                  <CardTitle>{job.title}</CardTitle>
                 <CardDescription>
  {job.createdAt.toLocaleDateString("tr-TR", {
    year: "numeric",
    month: "long",
    day: "numeric"
  })} tarihinde paylaşıldı
</CardDescription>

                </CardHeader>
                <CardContent className="flex-grow">
                  <p className="text-sm text-muted-foreground line-clamp-3">{job.description}</p>
                </CardContent>
                <CardFooter className="flex justify-between items-center">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Users className="mr-2 h-4 w-4" />
                    {candidateCount} başvuru
                  </div>
                  <Link href={`/jobs/${job.id}`}>
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
