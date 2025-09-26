import apiClient from './base';
import { AxiosResponse } from 'axios';


// Backend Veri Modelleri İçin Ön Uç Şemaları

/**
 * İş Deneyimi detaylarını tanımlar.
 */
export interface WorkExperience {
    /** İş unvanı. */
    job_title: string;
    /** Şirket adı. */
    company_name: string;
    /** Başlangıç tarihi (YYYY-MM-DD). */
    start_date: string;
    /** Bitiş tarihi (YYYY-MM-DD) veya halen çalışılıyorsa null. */
    end_date: string | null;
    /** Halen bu pozisyonda çalışılıp çalışılmadığı. */
    is_current: boolean;
    /** İş tanımı. */
    description: string;
}

/**
 * Eğitim Geçmişi detaylarını tanımlar.
 */
export interface EducationHistory {
    /** Kurumun adı. */
    institution_name: string;
    /** Kazanılan derece (örn: Lisans, Yüksek Lisans). */
    degree: string;
    /** Çalışma alanı/bölümü. */
    field_of_study: string;
    /** Başlangıç tarihi (YYYY-MM-DD). */
    start_date: string;
    /** Bitiş tarihi (YYYY-MM-DD) veya halen devam ediyorsa null. */
    end_date: string | null;
}

/**
 * Sertifika bilgilerini tanımlar.
 */
export interface Certification {
    /** Sertifikanın adı. */
    name: string;
    /** Sertifikayı veren kurum. */
    issuing_organization: string;
    /** Veriliş tarihi (YYYY-MM-DD). */
    issue_date: string;
}

/**
 * Dil ve yeterlilik seviyesini tanımlar.
 */
export interface Language {
    /** Dilin adı. */
    language: string;
    /** Dil yeterlilik seviyesi. */
    proficiency: 'beginner' | 'intermediate' | 'advanced' | 'fluent' | 'native';
}

/**
 * Başvuru (Application) nesnesinin tamamını tanımlar.
 */
export interface Application {
    /** Başvurunun tekil kimliği (UUID). */
    application_id: string;

    /** Bağlı olduğu iş ilanının ID'si. */
    job_id: string;

    /** Başvuran adayın ID'si. */
    applicant_id: string;

    /** Başvuru tarihi (YYYY-MM-DD). */
    application_date: string;

    /** Başvurunun mevcut durumu. */
    status: 'RECEIVED' | 'IN_REVIEW' | 'REJECTED' | 'SHORTLISTED' | 'HIRED';

    /** Özgeçmiş dosyasının yolu. */
    resume_file_path: string | null;

    /** Özgeçmişin yazıldığı dil. */
    resume_language: string | null;

    /** Toplam deneyim yılı. */
    total_years_experience: number | null;

    /** Özgeçmişten ayrıştırılmış yetenekler. */
    parsed_skills: string[] | null;

    /** Adayın sertifikaları. */
    certifications: Certification[] | null;

    /** Adayın konuşma dilleri. */
    languages: Language[] | null;

    /** Ayrıştırılmış ham özgeçmiş metni. */
    parsed_resume_data: string | null;

    /** İş ilanıyla eşleşme puanı. */
    ranking_score: number | null;

    /** İş deneyimi geçmişi listesi. */
    work_experience: WorkExperience[] | null;

    /** Eğitim geçmişi listesi. */
    education_history: EducationHistory[] | null;
}

/**
 * Yeni bir başvuru oluşturmak için kullanılan veri yapısı.
 * Sunucu tarafından oluşturulan alanlar çıkarılmıştır.
 */
export interface ApplicationCreate extends Omit<Application, 'application_id' | 'application_date' | 'status' | 'ranking_score'> {
    /** Başlangıç durumu (İsteğe bağlı). */
    status?: 'RECEIVED' | 'IN_REVIEW' | 'REJECTED' | 'SHORTLISTED' | 'HIRED';
}


// API Fonksiyonları

/**
 * Sunucudaki tüm başvuruları getirir.
 * @returns Başvuruların listesini içeren Promise.
 */
export const getApplications = (): Promise<AxiosResponse<Application[]>> => {
    return apiClient.get('/applications');
};

/**
 * Belirtilen ID'ye sahip tek bir başvuruyu getirir.
 * * @param id Başvurunun UUID'si.
 * @returns Başvuru nesnesini içeren Promise.
 */
export const getApplicationById = (id: string): Promise<AxiosResponse<Application>> => {
    return apiClient.get(`/applications/${id}`);
};

/**
 * Belirli bir adaya ait tüm başvuruları getirir.
 * * @param applicantId Adayın UUID'si.
 * @returns Başvuruların listesini içeren Promise.
 */
export const getApplicationsByApplicant = (applicantId: string): Promise<AxiosResponse<Application[]>> => {
    return apiClient.get(`/applications/by-applicant/${applicantId}`);
};

/**
 * Belirli bir iş ilanına yapılan tüm başvuruları getirir.
 * * @param jobId İş ilanının UUID'si.
 * @returns Başvuruların listesini içeren Promise.
 */
export const getApplicationsForJob = (jobId: string): Promise<AxiosResponse<Application[]>> => {
    return apiClient.get(`/applications/by-job/${jobId}`);
};

/**
 * Sunucuda yeni bir başvuru kaydı oluşturur.
 * * @param application Yeni başvuruya ait veriler.
 * @returns Oluşturulan Başvuru nesnesini içeren Promise.
 */
export const createApplication = (application: ApplicationCreate): Promise<AxiosResponse<Application>> => {
    return apiClient.post('/applications', application);
};

/**
 * Bir başvurunun durumunu günceller.
 * * @param applicationId Güncellenecek başvurunun UUID'si.
 * @param newStatus Başvuru için ayarlanacak yeni durum.
 * @returns Güncellenmiş Başvuru nesnesini içeren Promise.
 */
export const updateApplicationStatus = (applicationId: string, newStatus: Application['status']): Promise<AxiosResponse<Application>> => {
    return apiClient.put(`/applications/${applicationId}/status?new_status=${newStatus}`);
};

/**
 * Tek bir başvuru için eşleşme puanını yeniden hesaplar.
 * * @param applicationId Güncellenecek başvurunun UUID'si.
 * @returns Yeniden hesaplanmış puana sahip Başvuru nesnesini içeren Promise.
 */
export const recalculateSingleApplicationRank = (applicationId: string): Promise<AxiosResponse<Application>> => {
    return apiClient.post(`/applications/${applicationId}/recalculate-rank`);
};

/**
 * Belirli bir iş ilanına ait tüm başvuruların eşleşme puanlarını yeniden hesaplar.
 * * @param jobId İş ilanının UUID'si.
 * @returns Yeniden hesaplanmış puana sahip başvuruların listesini içeren Promise.
 */
export const recalculateApplicationsForJobRank = (jobId: string): Promise<AxiosResponse<Application[]>> => {
    return apiClient.post(`/applications/by-job/${jobId}/recalculate-ranks`);
};
