import axios from 'axios';
import Cookies from 'js-cookie';

// Ortam değişkenlerinden temel API URL'sini alır.
const base_url = process.env.NEXT_PUBLIC_API_BASEURL;

/**
 * Tüm API istekleri için yapılandırılmış ana Axios istemcisi.
 * Temel URL'yi ayarlar ve Content-Type başlıklarını tanımlar.
 */
const apiClient = axios.create({
    baseURL: base_url,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

/**
 * İstek kesicisi (Interceptor).
 * Her giden isteğe, Session Storage'da kayıtlı olan erişim belirtecini (access_token)
 * 'Authorization: Bearer [token]' başlığı olarak otomatik ekler.
 */
apiClient.interceptors.request.use(
    (config) => {
        const token = sessionStorage.getItem('access_token');

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/**
 * Yanıt kesicisi (Interceptor).
 * Sunucudan gelen yanıtları dinler. Eğer yanıt durumu 401 (Yetkisiz) ise,
 * kaydedilen tüm oturum verilerini temizler ve kullanıcıyı '/login' sayfasına yönlendirir.
 */
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response?.status === 401) {
            sessionStorage.removeItem('access_token');
            sessionStorage.removeItem('user_data');

            Cookies.remove('access_token');
            Cookies.remove('user_data');

            if (typeof window !== 'undefined') {
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

export default apiClient;