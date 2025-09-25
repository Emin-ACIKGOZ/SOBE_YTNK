"use client";

import { useToast } from "@/hooks/use-toast";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { CvUpload } from "@/components/cv-upload";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { getJob } from "@/lib/api";
import { updateApplicationStatus, Application } from "@/lib/api/applications";
import { getRankings, getResumeRankings, ranking } from "@/lib/api/ranking";
import { ArrowLeft, Briefcase, Building2, Calendar, Clock, Code, DollarSign, FileText, GraduationCap, Loader2, MapPin, Star, User, Users } from "lucide-react";

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

// Candidate veri yapısı
interface Candidate {
  resume_language: string;
  total_years_experience: number;
  parsed_skills: string[];
  certifications: any[];
  languages: any[];
  parsed_resume_data: string;
  status: string;
  ranking_score: number;
  application_id: string;
  applicant_id: string;
  job_id: string;
  application_date: string;
  resume_file_path: string;
  work_experience: WorkExperience[];
  education_history: Education[];
}

interface WorkExperience {
  job_title: string;
  company: string;
  start_date: string;
  end_date: string;
  description: string;
  id: string;
  application_id: string;
}

interface Education {
  degree: string;
  institution: string;
  start_date: string;
  end_date: string;
  location: string | null;
  id: string;
  application_id: string;
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

const STATUS_LABELS: Record<string, string> = {
  'RECEIVED': 'Başvuru Alındı',
  'IN_REVIEW': 'İncelemede',
  'SHORTLISTED': 'Kısa Listede',
  'HIRED': 'İşe Alındı',
  'REJECTED': 'Reddedildi',
};

// Candidate Card component
const CandidateCard = ({ candidate, onStatusChange }: { candidate: Candidate; onStatusChange: (applicationId: string, newStatus: string) => void }) => {
  const [pdfData, setPdfData] = useState<string | null>(null);
  const [isLoadingPdf, setIsLoadingPdf] = useState(false);
  const [showPdf, setShowPdf] = useState(false);
  const [isSkillsListOpen, setIsSkillsListOpen] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { toast } = useToast();

  // CV'den adayın ismini çıkarma fonksiyonu
  const extractNameFromCV = (cvData: string): string => {
    const lines = cvData.split('\n');
    // İlk satırda genellikle isim bulunur
    const firstLine = lines[0]?.trim();
    if (firstLine && firstLine.length < 50 && !firstLine.includes('@') && !firstLine.includes('http')) {
      return firstLine;
    }
    return 'Aday';
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('tr-TR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-blue-600 bg-blue-50';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getScoreText = (score: number) => {
    if (score >= 0.8) return 'Mükemmel Eşleşme';
    if (score >= 0.6) return 'İyi Eşleşme';
    if (score >= 0.4) return 'Orta Eşleşme';
    return 'Düşük Eşleşme';
  };

  const handleViewCV = async () => {
    try {
      console.log('=== CV Görüntüle Tıklandı ===');
      console.log('Aday ID:', candidate.applicant_id);
      console.log('================================');

      setIsLoadingPdf(true);

      const response = await getResumeRankings(candidate.application_id);

      console.log('=== API Yanıtı ===');
      console.log('Response:', response);
      console.log('==================');

      // The API returns a Base64 string directly.
      const base64Data = response.data;

      if (base64Data) {
        const dataUri = `data:application/pdf;base64,${base64Data}`;
        setPdfData(dataUri);
        setShowPdf(true);

        console.log('PDF URL oluşturuldu:', dataUri);
      } else {
        console.error('PDF verisi bulunamadı');
        toast({
          variant: "destructive",
          title: "PDF Yükleme Hatası",
          description: "PDF verisi bulunamadı. Lütfen tekrar deneyin.",
        });
      }

    } catch (error) {
      console.error('=== CV Görüntüle Hatası ===');
      console.error('Aday ID:', candidate.applicant_id);
      console.error('Hata:', error);
      console.error('==========================');
      toast({
        variant: "destructive",
        title: "PDF Yükleme Hatası",
        description: "CV yüklenirken bir hata oluştu. Lütfen tekrar deneyin.",
      });
    } finally {
      setIsLoadingPdf(false);
    }
  };

  const handleClosePdf = () => {
    setShowPdf(false);
    if (pdfData) {
      setPdfData(null);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    try {
      await updateApplicationStatus(candidate.application_id, newStatus as Application['status']);
      toast({
        title: "Durum Güncellendi",
        description: `Adayın durumu başarıyla "${STATUS_LABELS[newStatus]}" olarak güncellendi.`,
      });
      setIsDialogOpen(false);
      onStatusChange(candidate.application_id, newStatus);
    } catch (error) {
      console.error("Error updating status:", error);
      toast({
        variant: "destructive",
        title: "Durum Güncelleme Hatası",
        description: "Durum güncellenirken bir hata oluştu. Lütfen tekrar deneyin.",
      });
    }
  };

  const candidateName = extractNameFromCV(candidate.parsed_resume_data);

  // Yetenekleri ayırma
  const visibleSkills = candidate.parsed_skills.slice(0, 6);
  const hiddenSkills = candidate.parsed_skills.slice(6);
  const shouldShowToggleButton = candidate.parsed_skills.length > 6;

  const toggleSkills = () => {
    setIsSkillsListOpen(!isSkillsListOpen);
  };

  // Dinamik geçiş sürelerini belirlemek için stil hesaplaması
  const transitionDuration = isSkillsListOpen
    ? 'max-height 500ms ease-in-out, opacity 500ms ease-in-out' // Fade In (500ms)
    : 'max-height 250ms ease-in-out, opacity 250ms ease-in-out'; // Fade Out (250ms)

  return (
    <div className="space-y-4">
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                {candidateName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()}
              </div>
              <div>
                <CardTitle className="text-lg font-semibold">{candidateName}</CardTitle>
                <CardDescription className="flex items-center gap-2 mt-1">
                  <User className="h-3 w-3" />
                  <span className="text-xs">ID: {candidate.applicant_id}</span>
                </CardDescription>
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(candidate.ranking_score)}`}>
              <div className="flex items-center gap-1">
                <Star className="h-3 w-3" />
                {Math.round(candidate.ranking_score * 100)}%
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-4">
            {/* Eşleşme durumu */}
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={getScoreColor(candidate.ranking_score)}>
                {getScoreText(candidate.ranking_score)}
              </Badge>
              <Badge variant="secondary">
                {candidate.total_years_experience} yıl deneyim
              </Badge>
            </div>

            {/* Temel bilgiler */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Calendar className="h-3 w-3" />
                <span>Başvuru: {formatDate(candidate.application_date)}</span>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <FileText className="h-3 w-3" />
                <span>Durum: {STATUS_LABELS[candidate.status] || candidate.status}</span>
              </div>
            </div>

            {/* Eğitim bilgileri */}
            {candidate.education_history?.length > 0 && (
              <div className="flex flex-col gap-2 text-sm text-muted-foreground">
                {candidate.education_history.map((edu: any, index: number) => (
                  <div key={index} className="flex items-center gap-2">
                    <GraduationCap className="h-3 w-3" />
                    <span>
                      {edu.degree} - {edu.institution}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Tüm deneyimler */}
            {candidate.work_experience?.length > 0 && (
              <div className="flex flex-col gap-2 text-sm text-muted-foreground">
                {candidate.work_experience.map((exp: any, index: number) => (
                  <div key={index} className="flex items-center gap-2">
                    <Briefcase className="h-3 w-3" />
                    <span>
                      {exp.job_title} ({formatDate(exp.start_date)} - {formatDate(exp.end_date)})
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Yetenekler */}
            {candidate.parsed_skills.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Code className="h-3 w-3 text-muted-foreground" />
                  <span className="text-xs font-medium text-muted-foreground">Yetenekler</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {/* Her zaman görünür olan ilk 6 yetenek */}
                  {visibleSkills.map((skill, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {skill}
                    </Badge>
                  ))}

                  {/* Yeni eklenen/gizlenen yetenekler ve animasyon */}
                  {hiddenSkills.length > 0 && (
                    <div
                      className={`
                        flex flex-wrap gap-1 overflow-hidden
                      `}
                      style={{
                        // Değişiklik: Transition süresi duruma göre dinamik ayarlandı
                        transition: transitionDuration,
                        maxHeight: isSkillsListOpen ? '500px' : '0px',
                        opacity: isSkillsListOpen ? '1' : '0',
                        pointerEvents: isSkillsListOpen ? 'auto' : 'none',
                      }}
                    >
                      {/* Animasyon için DOM'da kalması gerekir */}
                      {hiddenSkills.map((skill, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* Göster/Gizle butonu */}
                  {shouldShowToggleButton && (
                    <Badge
                      variant="outline"
                      className="text-xs cursor-pointer"
                      onClick={toggleSkills}
                    >
                      {isSkillsListOpen ? 'Daha az göster' : `+${hiddenSkills.length} daha`}
                    </Badge>
                  )}
                </div>
              </div>
            )}

            {/* Aksiyon butonları */}
            <div className="flex gap-2 pt-2 border-t">
              {showPdf ? (
                // Show only the "Close PDF" button when PDF is open, and make it full width
                <Button
                  size="sm"
                  className="w-full"
                  variant="secondary"
                  onClick={handleClosePdf}
                >
                  PDF'yi Kapat
                </Button>
              ) : (
                // Show both buttons when PDF is not open
                <>
                  <Button
                    size="sm"
                    className="flex-1"
                    variant="outline"
                    onClick={handleViewCV}
                    disabled={isLoadingPdf}
                  >
                    {isLoadingPdf ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Yükleniyor...
                      </div>
                    ) : (
                      "CV'yi Görüntüle"
                    )}
                  </Button>
                  <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                      <Button size="sm" className="flex-1">
                        Durum Değiştir
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Başvuru Durumunu Güncelle</DialogTitle>
                        <DialogDescription>
                          {candidateName} adlı adayın başvuru durumunu buradan değiştirebilirsiniz.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="py-4 space-y-4">
                        <Select onValueChange={handleStatusChange} value={candidate.status}>
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Durum Seçin" />
                          </SelectTrigger>
                          <SelectContent>
                            {Object.entries(STATUS_LABELS).map(([key, label]) => (
                              <SelectItem key={key} value={key}>
                                {label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </DialogContent>
                  </Dialog>
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* PDF Görüntüleyici */}
      {showPdf && pdfData && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">{candidateName} - CV</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="w-full h-[800px] border rounded-lg overflow-hidden">
              <iframe
                src={pdfData}
                width="100%"
                height="100%"
                title={`${candidateName} CV`}
                className="border-0"
              />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default function JobDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [job, setJob] = useState<Job | null>(null);
  const [isJobLoading, setIsJobLoading] = useState(true);
  const [jobError, setJobError] = useState<string | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);

  const jobId = Array.isArray(params.id) ? params.id[0] : params.id;

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

    const getCandidatesForJob = async () => {
      try {
        const response = await getRankings(jobId);
        // Skora göre sırala
        const sortedCandidates = (response.data as Candidate[]).sort((a, b) => b.ranking_score - a.ranking_score);
        setCandidates(sortedCandidates);
      } catch (error) {
        console.error("Error fetching candidates:", error);
        // Adayları yüklerken hata olsa bile, iş ilanını göstermeye devam et
      }
    };

    fetchJob();
    getCandidatesForJob();
  }, [jobId]);

  const handleFileUpload = async (cvDataUri: string, file: File) => {
    if (!job) return;

    setIsLoading(true);
    try {
      const rankingResult = await ranking(job.job_id, file);
      console.log('Ranking API response:', rankingResult);

      // Adayları yeniden yükle
      const response = await getRankings(job.job_id);
      // Skora göre sırala
      const sortedCandidates = (response.data as Candidate[]).sort((a, b) => b.ranking_score - a.ranking_score);
      setCandidates(sortedCandidates);

      toast({
        title: "CV İşlendi",
        description: `${file.name} başarıyla analiz edildi ve sıralandı.`,
      });
    } catch (error) {
      console.error("File upload failed:", error);
      toast({
        variant: "destructive",
        title: "Yükleme Başarısız",
        description: "CV yüklenirken bir hata oluştu. Lütfen tekrar deneyin.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleStatusChange = (applicationId: string, newStatus: string) => {
    setCandidates(prevCandidates =>
      prevCandidates.map(c =>
        c.application_id === applicationId ? { ...c, status: newStatus } : c
      )
    );
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
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="font-headline">Eşleşen Adaylar</CardTitle>
                  <CardDescription>Bu pozisyona başvuran adaylar, eşleşme skoruna göre sıralanmıştır.</CardDescription>
                </div>
                {candidates.length > 0 && (
                  <Badge variant="secondary">
                    {candidates.length} aday
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {candidates.length > 0 ? (
                <div className="space-y-4">
                  {candidates
                    .map((candidate) => (
                      <CandidateCard
                        key={candidate.application_id}
                        candidate={candidate}
                        onStatusChange={handleStatusChange}
                      />
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
