import axios from 'axios';
import type {
  JobResponse,
  CreateJobResponse,
  HealthResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Accept': 'application/json',
  },
});

export async function createJob(formData: FormData): Promise<CreateJobResponse> {
  const response = await apiClient.post<CreateJobResponse>('/api/v1/jobs', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

export async function getJob(jobId: string): Promise<JobResponse> {
  const response = await apiClient.get<JobResponse>(`/api/v1/jobs/${jobId}`);
  return response.data;
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>('/api/v1/health');
  return response.data;
}

export { API_BASE_URL };