import apiClient from './base';
import { AxiosResponse } from 'axios';

// --- Aday Sıralama ve Özgeçmiş Analiz Türleri ---

/**
 * İş deneyimi detaylarını tanımlar.
 * (Backend şeması netleşene kadar genişletilebilir tip).
 */
interface WorkExperience extends Record<string, any> { }

/**
 * Eğitim geçmişi detaylarını tanımlar.
 * (Backend şeması netleşene kadar genişletilebilir tip).
 */
interface EducationHistory extends Record<string, any> { }

/**
 * Özgeçmiş Analizi ve Sıralama yanıtının yapısını tanımlar.
 */
interface RankingResponse {
    /** Özgeçmişin yazıldığı dil. */
    resume_language: string;
    /** Özgeçmişte belirtilen toplam deneyim yılı. */
    total_years_experience: number;
    /** Özgeçmişten ayrıştırılmış yetenekler listesi. */
    parsed_skills: string[];
    /** Özgeçmişten ayrıştırılmış sertifikalar listesi. */
    certifications: string[];
    /** Özgeçmişten ayrıştırılmış diller listesi. */
    languages: string[];
    /** Özgeçmişin ayrıştırılmış ham metin verisi. */
    parsed_resume_data: string;
    /** Sıralama işleminin durumu. */
    status: "RECEIVED" | "PROCESSING" | "COMPLETED" | "FAILED";
    /** İş ilanına göre hesaplanan sıralama puanı. */
    ranking_score: number;
    /** İlgili başvurunun ID'si. */
    application_id: string;
    /** Başvuran adayın ID'si. */
    applicant_id: string;
    /** Başvurunun yapıldığı iş ilanının ID'si. */
    job_id: string;
    /** Başvurunun yapıldığı tarih. */
    application_date: string;
    /** Özgeçmiş dosyasının sunucudaki yolu. */
    resume_file_path: string;
    /** Ayrıştırılmış iş deneyimi listesi. */
    work_experience: WorkExperience[];
    /** Ayrıştırılmış eğitim geçmişi listesi. */
    education_history: EducationHistory[];
}

// --- Özgeçmiş Sıralama API Fonksiyonları ---

/**
 * Belirtilen iş ilanı için bir özgeçmiş dosyasını yükler ve sıralama işlemini başlatır.
 * İstek `multipart/form-data` formatında gönderilir.
 * * @param jobId Özgeçmişin eşleştirileceği iş ilanının UUID'si.
 * @param file Yüklenecek özgeçmiş dosyası (File nesnesi).
 * @returns Sıralama işleminin sonuçlarını içeren Promise.
 */
export const ranking = (jobId: string, file: File): Promise<AxiosResponse<RankingResponse>> => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/ranking/process/${jobId}`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};


/**
 * Belirli bir iş ilanına ait tüm özgeçmiş sıralama sonuçlarını (başvuruları) getirir.
 * * @param jobId Sıralama sonuçları istenecek iş ilanının UUID'si.
 * @returns Sıralama yanıtı nesneleri dizisini içeren Promise.
 */
export const getRankings = (jobId: string): Promise<AxiosResponse<RankingResponse[]>> => {
    return apiClient.get(`/ranking/${jobId}`);
}

/**
 * Belirli bir başvuruya ait özgeçmiş dosyasının ham metin içeriğini getirir.
 * * @param applicationId Özgeçmiş metni istenecek başvurunun UUID'si.
 * @returns Özgeçmişin ham metin içeriğini (string) içeren Promise.
 */
export const getResumeRankings = (applicationId: string): Promise<AxiosResponse<string>> => {
    return apiClient.get(`/ranking/resume/${applicationId}`);
}


// --- Dışa Aktarılan Türler ---
export type { RankingResponse, WorkExperience, EducationHistory };