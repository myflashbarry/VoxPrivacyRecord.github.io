/**
 * API service layer for backend communication.
 */
import axios, { AxiosError } from 'axios';
import type { LoginResponse, NextTaskResponse, UploadResponse } from '../types';

// Get API base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export class ApiError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Handle API errors consistently.
 */
function handleApiError(error: unknown): never {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    const message = axiosError.response?.data?.detail || axiosError.message || 'Unknown error';
    throw new ApiError(message, axiosError.response?.status);
  }
  throw new ApiError(error instanceof Error ? error.message : 'Unknown error');
}

/**
 * Login or create a new user.
 */
export async function login(username: string): Promise<LoginResponse> {
  try {
    const formData = new FormData();
    formData.append('username', username);
    
    const response = await api.post<LoginResponse>('/api/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * Get the next recording task for a user.
 */
export async function getNextTask(username: string): Promise<NextTaskResponse> {
  try {
    const response = await api.get<NextTaskResponse>('/api/next_task', {
      params: { username },
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * Upload a recording to the backend.
 */
export async function uploadRecording(
  username: string,
  language: string,
  taskType: string,
  role: string,
  itemId: string,
  audioBlob: Blob
): Promise<UploadResponse> {
  try {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('language', language);
    formData.append('task_type', taskType);
    formData.append('role', role);
    formData.append('item_id', itemId);
    formData.append('audio', audioBlob, 'recording.webm');
    
    const response = await api.post<UploadResponse>('/api/upload_recording', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
}

/**
 * Test backend connection.
 */
export async function testConnection(): Promise<boolean> {
  try {
    await api.get('/');
    return true;
  } catch {
    return false;
  }
}

