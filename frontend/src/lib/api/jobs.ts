import apiClient from './base';
import { AxiosResponse } from 'axios';

// --- İş İlanı Türleri ---

// Backend SeniorityLevel (Python Enum):
// INTERNSHIP, ENTRY_LEVEL, JUNIOR_LEVEL, MID_LEVEL, SENIOR_LEVEL, DIRECTOR, EXECUTIVE

// Backend EmploymentType (Python Enum):
// FULL_TIME, PART_TIME, CONTRACT, INTERNSHIP

/**
 * API'den dönen tam İş İlanı (JobPosting) nesnesi için arayüz.
 */
export interface JobPosting {
  /** İş ilanının tekil kimliği (UUID). */
  job_id: string;

  /** İş ilanının başlığı. */
  title: string;

  /** Şirket adı. */
  company_name: string;

  /** Çalışma konumu. */
  location: string;

  /** Deneyim seviyesi. (BACKEND ALIGNMENT) */
  seniority_level:
    | 'INTERNSHIP'
    | 'ENTRY_LEVEL'
    | 'JUNIOR_LEVEL'
    | 'MID_LEVEL'
    | 'SENIOR_LEVEL'
    | 'DIRECTOR'
    | 'EXECUTIVE';

  /** İstihdam türü. (BACKEND ALIGNMENT) */
  employment_type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'INTERNSHIP';

  /** İşin genel tanımı. */
  description: string;

  /** Çalışanın sorumlulukları listesi. */
  responsibilities: string[];

  /** Adaydan beklenen nitelikler listesi. */
  qualifications: string[];

  /** Gerekli yetenekler listesi. */
  required_skills: string[];

  /** Maaş bilgisi (isteğe bağlı). */
  salary?: string;

  /** İlanın yayınlanma tarihi. */
  posted_at?: string;

  /** İlanın son güncellenme tarihi. */
  updated_at?: string;

  /** İlanın aktif olup olmadığını gösterir (soft-delete için). */
  is_active: boolean;
}

/**
 * Yeni bir iş ilanı oluşturmak için gerekli yük (payload).
 * Sunucu tarafından üretilen alanlar (ID, tarihler, is_active) hariç tutulur.
 */
export interface JobCreatePayload {
  title: string;
  company_name: string;
  location: string;
  /** Deneyim seviyesi. (BACKEND ALIGNMENT) */
  seniority_level:
    | 'INTERNSHIP'
    | 'ENTRY_LEVEL'
    | 'JUNIOR_LEVEL'
    | 'MID_LEVEL'
    | 'SENIOR_LEVEL'
    | 'DIRECTOR'
    | 'EXECUTIVE';
  /** İstihdam türü. (BACKEND ALIGNMENT) */
  employment_type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'INTERNSHIP';
  description: string;
  responsibilities: string[];
  qualifications: string[];
  required_skills: string[];
  salary?: string;
}

/**
 * Tüm iş ilanları listesi API yanıtı için arayüz (Sayfalama verileri dahil).
 */
export interface JobsListResponse {
  /** İş ilanı listesi. */
  jobs: JobPosting[];

  /** Toplam ilan sayısı. */
  total: number;

  /** Mevcut sayfa numarası. */
  page: number;

  /** Sayfa başına düşen öğe sayısı. */
  per_page: number;
}

// --- İş İlanı API Fonksiyonları ---

/**
 * Sunucuda yeni bir iş ilanı oluşturur.
 * * @param jobData Yeni iş ilanına ait veriler.
 * @returns Oluşturulan İş İlanı nesnesini içeren Promise.
 */
export const createJob = (
  jobData: JobCreatePayload,
): Promise<AxiosResponse<JobPosting>> => {
  return apiClient.post('/jobs/', jobData);
};

/**
 * İş ilanlarının listesini sayfalama (pagination) parametreleriyle getirir.
 * Arka planda aktif olmayan ilanları filtreler.
 * * @param params Atlanacak (skip) ve sınırlandırılacak (limit) öğe sayıları (isteğe bağlı).
 * @returns İş İlanı nesneleri dizisini içeren Promise.
 */
export const getJobs = (params?: {
  skip?: number;
  limit?: number;
}): Promise<AxiosResponse<JobPosting[]>> => {
  return apiClient.get('/jobs/', { params });
};

/**
 * Belirtilen ID'ye sahip tek bir iş ilanını getirir.
 * * @param id İş ilanının UUID'si.
 * @returns İş İlanı nesnesini içeren Promise.
 */
export const getJob = (id: string): Promise<AxiosResponse<JobPosting>> => {
  return apiClient.get(`/jobs/${id}`);
};

/**
 * Mevcut bir iş ilanının bilgilerini günceller.
 * * @param id Güncellenecek iş ilanının UUID'si.
 * @param jobData Güncellenecek alanları içeren kısmi veri.
 * @returns Güncellenmiş İş İlanı nesnesini içeren Promise.
 */
export const updateJob = (
  id: string,
  jobData: Partial<JobCreatePayload>,
): Promise<AxiosResponse<JobPosting>> => {
  return apiClient.put(`/jobs/${id}`, jobData);
};

/**
 * Belirtilen ID'ye sahip iş ilanını pasif hale getirir (Soft Delete).
 * * @param id Silinecek iş ilanının UUID'si.
 * @returns İşlem başarılıysa (204 No Content) çözümlenen Promise.
 */
export const deleteJob = (id: string): Promise<AxiosResponse<void>> => {
  return apiClient.delete(`/jobs/${id}`);
};
