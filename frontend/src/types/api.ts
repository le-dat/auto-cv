// Types matching BE API contract

export interface MatchResult {
  score: number;
  matching_skills: string[];
  missing_skills: string[];
  strong_skills: string[];
  suggestions: string[];
  ats_keywords: string[];
}

export interface GenerateResult {
  cv_markdown: string;
  match_result: MatchResult;
  processing_time_ms: number;
  llm_model_used: string;
  context_sources: string[];
}

export interface JobResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'done' | 'failed';
  result: GenerateResult | null;
  error: string | null;
}

export interface CreateJobResponse {
  job_id: string;
  status: 'pending';
  message: string;
}

export interface HealthResponse {
  status: 'ok';
}

export type JobStatus = 'pending' | 'processing' | 'done' | 'failed';