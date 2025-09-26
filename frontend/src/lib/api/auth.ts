import apiClient from './base';

const base_url = process.env.NEXT_PUBLIC_API_BASEURL;

// --- Kimlik Doğrulama API Türleri ---

/**
 * Yeni kullanıcı kaydı için gerekli yük (payload).
 */
export interface SignupPayload {
  /** Kullanıcı adı. */
  username: string;

  /** E-posta adresi. */
  email: string;

  /** Kullanıcının rolü. */
  role: string;

  /** Parola. */
  password: string;
}

/**
 * Kullanıcı girişi için gerekli yük (payload).
 */
export interface LoginPayload {
  /** Kullanıcı adı. */
  username: string;

  /** Parola. */
  password: string;

  /** Yetki türü (Varsayılan: 'password'). */
  grant_type?: string;

  /** İstenen kapsam (scope). */
  scope?: string;

  /** İstemci kimliği. */
  client_id?: string;

  /** İstemci sırrı. */
  client_secret?: string;
}

/**
 * Giriş (login) işleminden dönen yanıt yapısı.
 */
export interface LoginResponse {
  /** Erişim belirteci (token). */
  access_token: string;

  /** Token türü. */
  token_type: string;

  /** Belirtecin geçerlilik süresi (saniye). */
  expires_in?: number;

  /** Yeni belirteç almak için kullanılacak yenileme belirteci. */
  refresh_token?: string;
}


// --- Kimlik Doğrulama API Fonksiyonları ---

/**
 * Yeni bir kullanıcı kaydı oluşturur.
 * * @param data Kayıt için gerekli kullanıcı verileri.
 * @returns Sunucudan gelen ham yanıt (Response).
 */
export const signup = async (data: SignupPayload): Promise<Response> => {
  const response = await fetch(`${base_url}/auth/signup`, {
    method: 'POST',
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return response;
};

/**
 * Kullanıcı kimlik bilgileriyle giriş yapar ve erişim belirteci alır.
 * Axios yerine fetch kullanılarak `application/x-www-form-urlencoded` formatında istek gönderilir.
 * * @param data Giriş için gerekli kullanıcı adı, parola ve isteğe bağlı parametreler.
 * @returns Sunucudan gelen ham yanıt (Response).
 */
export const login = async (data: LoginPayload): Promise<Response> => {
  const formBody = new URLSearchParams();
  formBody.append('grant_type', data.grant_type || 'password');
  formBody.append('username', data.username);
  formBody.append('password', data.password);
  formBody.append('scope', data.scope || '');
  formBody.append('client_id', data.client_id || '');
  formBody.append('client_secret', data.client_secret || '');

  const response = await fetch(`${base_url}/auth/token`, {
    method: 'POST',
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formBody.toString(),
  });

  return response;
};

/**
 * Oturum açmış kullanıcının profil bilgilerini yetkili bir istek ile (Axios) getirir.
 * @returns Profil verilerini içeren Promise.
 */
export const getProfile = () => apiClient.get('/auth/me');

/**
 * Yenileme belirteci (refresh token) kullanarak yeni bir erişim belirteci alır.
 * * @param refreshToken Geçerli yenileme belirteci.
 * @returns Yeni belirteç verilerini içeren Promise.
 */
export const refreshToken = (refreshToken: string) =>
  apiClient.post('/auth/refresh', { refresh_token: refreshToken });

/**
 * Kullanıcının oturumunu kapatır ve tüm oturum bilgilerini temizler.
 */
export const logout = async () => {
  try {
    await apiClient.post('/auth/logout');
  } catch (error) {
  } finally {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('user_data');
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }
};


// --- Yardımcı Fonksiyonlar ---

/**
 * Kimlik doğrulama belirteçlerini ve kullanıcı verilerini yöneten yardımcı fonksiyonlar.
 */
export const authUtils = {
  /**
   * Erişim belirtecini ve isteğe bağlı kullanıcı verilerini Session Storage'a kaydeder.
   * * @param token Erişim belirteci (access token).
   * @param userData Kullanıcıya ait ek veriler (JSON'a dönüştürülebilir).
   */
  saveToken: (token: string, userData?: any) => {
    sessionStorage.setItem('access_token', token);
    if (userData) {
      sessionStorage.setItem('user_data', JSON.stringify(userData));
    }
  },

  /**
   * Session Storage'dan kayıtlı erişim belirtecini alır.
   * @returns Erişim belirteci (string) veya bulunamazsa null.
   */
  getToken: () => {
    return sessionStorage.getItem('access_token');
  },

  /**
   * Kullanıcının oturum açıp açmadığını kontrol eder.
   * @returns Erişim belirteci varsa true, yoksa false.
   */
  isAuthenticated: () => {
    return !!sessionStorage.getItem('access_token');
  },

  /**
   * Session Storage'dan kayıtlı kullanıcı verilerini alır.
   * @returns Kullanıcı verileri (JSON'dan parse edilmiş) veya bulunamazsa null.
   */
  getUserData: () => {
    const userData = sessionStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  },
};