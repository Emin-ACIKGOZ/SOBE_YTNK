// lib/api/base.ts - Base API client
import axios from 'axios';
import Cookies from 'js-cookie';


const base_url = process.env.NEXT_PUBLIC_API_BASEURL;

// Base API client
const apiClient = axios.create({
    baseURL: base_url,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

// Request interceptor - her isteğe otomatik token ekler
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

// Response interceptor - 401 durumunda otomatik logout
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