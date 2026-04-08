import { create } from 'zustand';
import type { JobResponse, JobStatus } from '../types/api';
import { getJob, createJob } from '../lib/api';

interface JobState {
  currentJobId: string | null;
  jobStatus: JobStatus | null;
  jobResponse: JobResponse | null;
  isPolling: boolean;
  error: string | null;
  submitError: string | null;

  submitJob: (formData: FormData) => Promise<string>;
  pollJob: (jobId: string) => Promise<void>;
  stopPolling: () => void;
  reset: () => void;
}

export const useJobStore = create<JobState>((set, get) => ({
  currentJobId: null,
  jobStatus: null,
  jobResponse: null,
  isPolling: false,
  error: null,
  submitError: null,

  submitJob: async (formData: FormData) => {
    set({ submitError: null });
    try {
      const response = await createJob(formData);
      set({ currentJobId: response.job_id, jobStatus: 'pending', jobResponse: null, error: null });
      return response.job_id;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to submit job';
      set({ submitError: message });
      throw err;
    }
  },

  pollJob: async (jobId: string) => {
    set({ isPolling: true, error: null });
    try {
      const response = await getJob(jobId);
      set({
        jobStatus: response.status,
        jobResponse: response,
        isPolling: response.status === 'pending' || response.status === 'processing',
        error: response.status === 'failed' ? response.error : null,
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch job';
      set({ isPolling: false, error: message });
    }
  },

  stopPolling: () => {
    set({ isPolling: false });
  },

  reset: () => {
    set({
      currentJobId: null,
      jobStatus: null,
      jobResponse: null,
      isPolling: false,
      error: null,
      submitError: null,
    });
  },
}));