import apiClient from './base';
import { AxiosResponse } from 'axios';

// --- Aday Veri Yapıları ---

/**
 * API'den dönen tam Aday (Applicant) nesnesi için arayüz.
 */
export interface Applicant {
    /** Adayın tekil kimliği (UUID). */
    applicant_id: string;

    first_name: string;

    last_name: string;

    email: string;

    phone_number: string | null;

    linkedin_profile_url: string | null;

    github_profile_url: string | null;
}

/**
 * Yeni bir Aday oluşturmak için gerekli olan veriler.
 */
export interface ApplicantCreate {
    first_name: string;
    last_name: string;
    email: string;
    phone_number?: string | null;
    linkedin_profile_url?: string | null;
    github_profile_url?: string | null;
}

/**
 * Mevcut bir Adayı kısmen güncellemek için kullanılan veriler.
 * Tüm alanlar isteğe bağlıdır.
 */
export interface ApplicantUpdate {
    first_name?: string;
    last_name?: string;
    email?: string;
    phone_number?: string | null;
    linkedin_profile_url?: string | null;
    github_profile_url?: string | null;
}


// --- Aday API Fonksiyonları ---

const APPLICANTS_BASE_PATH = '/applicants';

/**
 * Yeni bir adayı sisteme kaydeder.
 * * @param applicantData Yeni adayın zorunlu ve isteğe bağlı verileri.
 * @returns Oluşturulan Aday nesnesini içeren bir Promise.
 */
export const createApplicant = (
    applicantData: ApplicantCreate
): Promise<AxiosResponse<Applicant>> => {
    return apiClient.post(APPLICANTS_BASE_PATH, applicantData);
};

/**
 * Belirtilen ID'ye sahip tek bir adayın detaylarını getirir.
 * * @param applicantId Getirilecek adayın UUID'si (string).
 * @returns Aday nesnesini içeren bir Promise.
 */
export const getApplicant = (
    applicantId: string
): Promise<AxiosResponse<Applicant>> => {
    return apiClient.get(`${APPLICANTS_BASE_PATH}/${applicantId}`);
};

/**
 * Adayların bir listesini getirir. Sayfalama parametreleri isteğe bağlıdır.
 * * @param skip Atlanacak (es geçilecek) kayıt sayısı (Varsayılan: 0).
 * @param limit Getirilecek maksimum kayıt sayısı (Varsayılan: 100).
 * @returns Aday nesnelerinden oluşan bir diziyi içeren Promise.
 */
export const getApplicants = (
    skip: number = 0,
    limit: number = 100
): Promise<AxiosResponse<Applicant[]>> => {
    return apiClient.get(APPLICANTS_BASE_PATH, {
        params: { skip, limit },
    });
};

/**
 * Mevcut bir adayın bilgilerini günceller.
 * * @param applicantId Güncellenecek adayın UUID'si (string).
 * @param updateData Güncellenecek alanları içeren kısmi veri.
 * @returns Güncellenmiş Aday nesnesini içeren bir Promise.
 */
export const updateApplicant = (
    applicantId: string,
    updateData: ApplicantUpdate
): Promise<AxiosResponse<Applicant>> => {
    return apiClient.put(`${APPLICANTS_BASE_PATH}/${applicantId}`, updateData);
};

/**
 * Belirtilen ID'ye sahip adayı sistemden siler.
 * * @param applicantId Silinecek adayın UUID'si (string).
 * @returns Başarılı silme durumunda (204 No Content) çözümlenen bir Promise.
 */
export const deleteApplicant = (
    applicantId: string
): Promise<AxiosResponse<void>> => {
    return apiClient.delete(`${APPLICANTS_BASE_PATH}/${applicantId}`);
};
