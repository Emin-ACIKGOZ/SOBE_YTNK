
/**
 * İş İlanı detaylarını tanımlar.
 */
export interface JobPosting {
  /** İş ilanının tekil kimliği (UUID). */
  id: string;

  /** İş ilanının başlığı. */
  title: string;

  /** İşin genel tanımı. */
  description: string;

  /** İş için gereken zorunlu şartlar ve nitelikler. */
  requirements: string;

  /** İlanın oluşturulma tarihi. */
  createdAt: Date;
}

/**
 * Bir iş ilanına başvuran adayı ve özgeçmiş eşleştirme sonuçlarını tanımlar.
 */
export interface Candidate {
  /** Aday/başvurunun tekil kimliği (UUID). */
  id: string;

  /** Başvurunun ait olduğu iş ilanının kimliği. */
  jobId: string;

  /** Yüklenen özgeçmiş dosyasının adı. */
  fileName: string;

  /** Özgeçmiş dosyasının Data URI formatındaki içeriği (örn: base64). */
  cvDataUri: string;

  /** İş ilanıyla özgeçmiş arasındaki eşleşme puanı. */
  matchScore: number;

  /** Eşleşme puanının detaylı gerekçesi. */
  reasoning: string;

  /** Başvurunun yapıldığı tarih. */
  createdAt: Date;
}
