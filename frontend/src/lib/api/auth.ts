// lib/api/auth.ts - Authentication API
import apiClient from './base';

const base_url = process.env.NEXT_PUBLIC_API_BASEURL;

// Auth API Types
export interface SignupPayload {
  username: string;
  email: string;
  role: string;
  password: string;
}

export interface LoginPayload {
  username: string;
  password: string;
  grant_type?: string;
  scope?: string;
  client_id?: string;
  client_secret?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
  refresh_token?: string;
}

// Auth API functions
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

// Profile bilgisi al (axios ile - otomatik auth)
export const getProfile = () => apiClient.get('/auth/me');

// Refresh token (eğer varsa)
export const refreshToken = (refreshToken: string) =>
  apiClient.post('/auth/refresh', { refresh_token: refreshToken });

// Logout
export const logout = async () => {
  try {
    await apiClient.post('/auth/logout');
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Her durumda local storage'ı temizle
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('user_data');
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }
};

// Utility functions
export const authUtils = {
  saveToken: (token: string, userData?: any) => {
    sessionStorage.setItem('access_token', token);
    if (userData) {
      sessionStorage.setItem('user_data', JSON.stringify(userData));
    }
  },

  getToken: () => {
    return sessionStorage.getItem('access_token');
  },

  isAuthenticated: () => {
    return !!sessionStorage.getItem('access_token');
  },

  getUserData: () => {
    const userData = sessionStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  },
};