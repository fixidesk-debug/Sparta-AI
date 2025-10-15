import apiClient from './client';
import { User, File, Query, AuthToken } from '../types';

// Auth endpoints
export const authApi = {
  register: (email: string, password: string, full_name?: string) =>
    apiClient.post<User>('/api/v1/auth/register', { email, password, full_name }),

  login: (username: string, password: string) =>
    apiClient.post<AuthToken>('/api/v1/auth/login', 
      new URLSearchParams({ username, password }),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    ),

  getMe: () => apiClient.get<User>('/api/v1/auth/me'),
};

// File endpoints
export const fileApi = {
  upload: (file: globalThis.File) => {
    const formData = new FormData();
    formData.append('file', file as any);
    return apiClient.post<File>('/api/v1/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  list: () => apiClient.get<File[]>('/api/v1/files/list'),

  get: (id: number) => apiClient.get<File>(`/api/v1/files/${id}`),

  delete: (id: number) => apiClient.delete(`/api/v1/files/${id}`),
};

// Query endpoints
export const queryApi = {
  ask: (query_text: string, file_id?: number) =>
    apiClient.post<Query>('/api/v1/query/ask', { query_text, file_id }),

  history: (limit: number = 20) =>
    apiClient.get<Query[]>('/api/v1/query/history', { params: { limit } }),

  get: (id: number) => apiClient.get<Query>(`/api/v1/query/${id}`),
};

// Visualization endpoints
export const vizApi = {
  generate: (
    file_id: number,
    viz_type: string,
    x_column?: string,
    y_column?: string,
    parameters?: any
  ) =>
    apiClient.post('/api/v1/viz/generate', {
      file_id,
      viz_type,
      x_column,
      y_column,
      parameters,
    }),
};

// Code execution endpoints
export const execApi = {
  run: (code: string, language: string = 'python', file_id?: number) =>
    apiClient.post('/api/v1/exec/run', { code, language, file_id }),
};
