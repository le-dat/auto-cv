import { useEffect, useRef } from 'react';
import { useJobStore } from '../store/jobStore';

const POLL_INTERVAL = 2000;

export function usePolling(jobId: string | null, enabled: boolean = true) {
  const pollJob = useJobStore((state) => state.pollJob);
  const isPolling = useJobStore((state) => state.isPolling);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!enabled || !jobId) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Poll immediately
    pollJob(jobId);

    intervalRef.current = setInterval(() => {
      pollJob(jobId);
    }, POLL_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [jobId, enabled, pollJob]);

  return { isPolling };
}