"use client";

import { useToast } from "@/hooks/use-toast";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState, useContext } from "react";

import { CvUpload } from "@/components/cv-upload";
import { Badge } from "@/components/ui/badge";
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

import { AppContext } from "@/context/app-context";
import { Applicant } from "@/lib/api/applicants";
import { Button } from "@/components/ui/button";

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

// YENİ FONKSİYON: Duruma göre renk döndür
const getStatusBadgeClass = (status: string): string => {
  switch (status) {
    case 'RECEIVED':
      return 'bg-gray-100 text-gray-700 hover:bg-gray-200'; // gray tone
    case 'IN_REVIEW':
      return 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'; // yellow
    case 'SHORTLISTED':
      return 'bg-blue-100 text-blue-700 hover:bg-blue-200'; // blue
    case 'HIRED':
      return 'bg-green-100 text-green-700 hover:bg-green-200'; // green
    case 'REJECTED':
      return 'bg-red-100 text-red-700 hover:bg-red-200'; // red
    default:
      return 'bg-gray-100 text-gray-700 hover:bg-gray-200';
  }
};

// YENİ FONKSİYON: Eşleşme skoruna göre renk döndür
const getScoreBadgeClass = (score: number): string => {
  if (score >= 0.8) return 'bg-green-100 text-green-700 hover:bg-green-200';
  if (score >= 0.6) return 'bg-blue-100 text-blue-700 hover:bg-blue-200';
  if (score >= 0.4) return 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200';
  return 'bg-red-100 text-red-700 hover:bg-red-200';
};

// GÜNCELLENMİŞ FONKSİYON: Deneyim yıllarına göre renk döndür
// (< 1: Gri, 1-3: Mavi, 3-6: Sarı, 6+: Mor)
const getExperienceBadgeClass = (years: number): string => {
  if (years > 6) {
    return 'bg-purple-100 text-purple-700 hover:bg-purple-200'; // 6+ years (Purple)
  }
  if (years > 3) {
    return 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'; // 3 to 6 years (Yellow)
  }
  if (years >= 1) {
    return 'bg-blue-100 text-blue-700 hover:bg-blue-200'; // 1 to 3 years (Blue)
  }
  return 'bg-gray-100 text-gray-700 hover:bg-gray-200'; // <1 year (Gray)
};

// 💡 ROBUSTLY UPDATED HELPER FUNCTION: Normalizes all words in a name string (e.g., "john william" -> "John William")
const normalizeName = (name: string): string => {
  if (!name) return '';

  return name
    .trim()
    .toLowerCase()
    .split(/\s+/) // Split by one or more spaces
    .map(word => {
      if (word.length === 0) return '';
      // Capitalize the first letter and keep the rest lowercased
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(' '); // Join the capitalized words back with a single space
};


// Candidate Card component
const CandidateCard = ({ candidate, applicant, onStatusChange }: { candidate: Candidate; applicant: Applicant; onStatusChange: (applicationId: string, newStatus: string) => void }) => {
  const [pdfData, setPdfData] = useState<string | null>(null);
  const [isLoadingPdf, setIsLoadingPdf] = useState(false);
  const [showPdf, setShowPdf] = useState(false);
  const [isSkillsListOpen, setIsSkillsListOpen] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { toast } = useToast();

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

  // 💡 USES NEW ROBUST LOGIC: Get the full name by normalizing and combining the first and last names.
  const candidateFirstName = normalizeName(applicant.first_name);
  const candidateLastName = normalizeName(applicant.last_name);
  const candidateName = `${candidateFirstName} ${candidateLastName}`.trim();

  // Yetenekleri ayırma
  const visibleSkills = candidate.parsed_skills.slice(0, 6);
  const hiddenSkills = candidate.parsed_skills.slice(6);
  const shouldShowToggleButton = candidate.parsed_skills.length > 6;

  const toggleSkills = () => {
    setIsSkillsListOpen(!isSkillsListOpen);
  };

  // 🟢 DEĞİŞİKLİK: Eski geçiş süresi değişkeni kaldırıldı. Transition doğrudan CSS'e eklenecek.

  return (
    <div className="space-y-4">
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                {/* Fallback to first two letters for initials if name is complex/empty */}
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
            {/* Skor etiketi, daha küçük kalabilir */}
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
            {/* Eşleşme durumu, Deneyim ve YENİ: Durum - Tümü text-sm yapıldı */}
            <div className="flex flex-wrap items-center gap-2">
              <Badge
                variant="default"
                className={`text-sm px-3 py-1 font-bold transition-colors duration-300 ${getStatusBadgeClass(candidate.status)}`}
              >
                {STATUS_LABELS[candidate.status] || candidate.status}
              </Badge>
              <Badge
                variant="outline"
                className={`text-sm px-3 py-1 transition-colors duration-300 ${getScoreBadgeClass(candidate.ranking_score)}`}
              >
                {getScoreText(candidate.ranking_score)}
              </Badge>
              <Badge
                variant="secondary"
                className={`text-sm px-3 py-1 transition-colors duration-300 ${getExperienceBadgeClass(candidate.total_years_experience)}`}
              >
                {candidate.total_years_experience} yıl deneyim
              </Badge>
            </div>

            {/* Temel bilgiler (Başvuru Tarihi) */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Calendar className="h-3 w-3" />
                {/* GÜNCELLEME: Başvuru kelimesi kalınlaştırıldı ve font boyutu text-sm yapıldı. */}
                <span className="text-sm font-semibold">
                  <span className="font-bold">Başvuru:</span> {formatDate(candidate.application_date)}
                </span>
              </div>

              {/* Durum buradaydı, yukarı taşındı */}
              <div className="col-span-1"></div>
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

            {/* Yetenekler (GÜNCELLENMİŞ YERLEŞİM) */}
            {candidate.parsed_skills.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Code className="h-3 w-3 text-muted-foreground" />
                  <span className="text-sm font-semibold text-muted-foreground">Yetenekler</span>
                </div>

                {/* Tüm Yetenekler için Ana Konteyner - flex-wrap ile aynı satırda devam etmesi sağlandı */}
                <div className="flex flex-wrap gap-1">

                  {/* Her zaman görünür olan ilk 6 yetenek */}
                  {visibleSkills.map((skill, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {skill}
                    </Badge>
                  ))}

                  {/* 🚀 MAX-HEIGHT TRANSITION BAŞLANGICI 🚀 */}
                  <div
                    className="flex flex-wrap gap-1 transition-all ease-in-out duration-300"
                    style={{
                      // 🎯 CRITICAL CHANGE: Use transitionDelay
                      transitionDelay: isSkillsListOpen
                        ? '125ms'           // Expanding: Start opacity instantly
                        : '0ms',        // Collapsing: Wait 200ms before starting opacity fade-out

                      // 💡 Add explicit properties to ensure the delay applies correctly
                      transitionProperty: 'max-height, opacity',

                      maxHeight: isSkillsListOpen ? '300px' : '0',
                      opacity: isSkillsListOpen ? '1' : '0',
                      overflow: 'hidden',
                      marginTop: isSkillsListOpen ? '0' : '0',
                    }}
                  >
                    {/* Artık her bir Badge kendi başına bir animasyon uygulamıyor */}
                    {hiddenSkills.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                  {/* 🚀 MAX-HEIGHT TRANSITION SONU 🚀 */}
                </div>

                {/* GÖSTER/GİZLE Butonu - Ayrı bir satırda ve sola hizalı */}
                {shouldShowToggleButton && (
                  <div className="mt-2"> {/* mt-2 (margin-top: 0.5rem) ile boşluk eklendi */}
                    <Badge
                      className="text-xs cursor-pointer bg-green-100 text-green-700 hover:bg-green-200 transition-colors duration-200"
                      onClick={toggleSkills}
                    >
                      {isSkillsListOpen ? 'Daha az göster' : `+${hiddenSkills.length} daha`}
                    </Badge>
                  </div>
                )}
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
                  CV'yi Kapat
                </Button>
              ) : (
                // Show both buttons when PDF is not open
                <>
                  <Button
                    size="sm"
                    className="flex-1"
                    onClick={handleViewCV}
                    disabled={isLoadingPdf}
                    variant="outline" // Changed to outline for secondary action
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
  const { getApplicantById } = useContext(AppContext)!; // 💡 UPDATED: Use getApplicantById from context
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
                    .map((candidate) => {
                      // 💡 GET APPLICANT DATA
                      const applicant = getApplicantById(candidate.applicant_id);

                      // Skip rendering if applicant data is not found (data loading issue or inconsistency)
                      if (!applicant) {
                        // Optionally render a placeholder or error card
                        return null;
                      }

                      return (
                        <CandidateCard
                          key={candidate.application_id}
                          candidate={candidate}
                          applicant={applicant}
                          onStatusChange={handleStatusChange}
                        />
                      );
                    })}
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