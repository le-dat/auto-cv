import { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { useJobStore } from '../store/jobStore';
import { usePolling } from '../hooks/usePolling';
import { ScoreDisplay } from '../components/results/ScoreDisplay';
import { Loader2, AlertCircle, CheckCircle, XCircle, Download, RefreshCw } from 'lucide-react';

export function ResultsPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const jobResponse = useJobStore((state) => state.jobResponse);
  const jobStatus = useJobStore((state) => state.jobStatus);
  const error = useJobStore((state) => state.error);
  const stopPolling = useJobStore((state) => state.stopPolling);
  const reset = useJobStore((state) => state.reset);

  const { isPolling } = usePolling(jobId ?? null, jobStatus === 'pending' || jobStatus === 'processing');

  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  if (!jobId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
        <h2>Invalid Job ID</h2>
        <Link to="/" className="mt-4 text-[var(--accent)] hover:underline">
          Go back to upload
        </Link>
      </div>
    );
  }

  if (error || jobStatus === 'failed') {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="max-w-md text-center space-y-4">
          <XCircle className="h-12 w-12 text-red-400 mx-auto" />
          <h2>Job Failed</h2>
          <p className="text-[var(--text)]">{error || jobResponse?.error || 'An unknown error occurred'}</p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-lg bg-[var(--accent)] text-white px-6 py-2 font-medium hover:opacity-90 transition-opacity"
          >
            <RefreshCw className="h-4 w-4" />
            Try Again
          </Link>
        </div>
      </div>
    );
  }

  if (jobStatus === 'pending' || jobStatus === 'processing' || !jobResponse) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <Loader2 className="h-12 w-12 text-[var(--accent)] animate-spin mb-4" />
        <h2>{jobStatus === 'processing' ? 'Processing Your CV' : 'Job Pending'}</h2>
        <p className="text-[var(--text)] mt-2">
          {jobStatus === 'processing'
            ? 'Our AI is analyzing and rewriting your CV...'
            : 'Waiting for processing to begin...'}
        </p>
        <p className="text-xs text-[var(--text)] mt-4 opacity-60">Job ID: {jobId}</p>
      </div>
    );
  }

  const { result } = jobResponse;
  if (!result) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <AlertCircle className="h-12 w-12 text-yellow-400 mb-4" />
        <h2>No Result Available</h2>
        <Link to="/" className="mt-4 text-[var(--accent)] hover:underline">
          Go back to upload
        </Link>
      </div>
    );
  }

  const downloadMarkdown = () => {
    const blob = new Blob([result.cv_markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `optimized-cv-${jobId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex-1 px-4 py-8 space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CheckCircle className="h-8 w-8 text-green-400" />
          <div>
            <h2>Optimization Complete</h2>
            <p className="text-sm text-[var(--text)]">
              Processed in {(result.processing_time_ms / 1000).toFixed(1)}s using {result.llm_model_used}
            </p>
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={downloadMarkdown}
            className="flex items-center gap-2 rounded-lg border border-[var(--border)] px-4 py-2 text-sm text-[var(--text)] hover:bg-[var(--social-bg)] transition-colors"
          >
            <Download className="h-4 w-4" />
            Download CV
          </button>
          <Link
            to="/"
            onClick={reset}
            className="flex items-center gap-2 rounded-lg bg-[var(--accent)] text-white px-4 py-2 text-sm font-medium hover:opacity-90 transition-opacity"
          >
            New Job
          </Link>
        </div>
      </div>

      {/* Score Display */}
      <ScoreDisplay matchResult={result.match_result} />

      {/* Context Sources */}
      {result.context_sources.length > 0 && (
        <div className="text-xs text-[var(--text)] opacity-60">
          <span>Context: </span>
          {result.context_sources.join(', ')}
        </div>
      )}

      {/* Rewritten CV */}
      <div className="space-y-3">
        <h3>Optimized CV</h3>
        <div className="rounded-lg border border-[var(--border)] bg-[var(--code-bg)] p-6 text-left">
          <ReactMarkdown
            className="prose prose-invert prose-sm max-w-none text-[var(--text-h)]"
            components={{
              h1: ({ children }) => <h1 className="text-2xl font-bold text-[var(--text-h)] mb-4">{children}</h1>,
              h2: ({ children }) => <h2 className="text-xl font-semibold text-[var(--text-h)] mt-6 mb-3">{children}</h2>,
              h3: ({ children }) => <h3 className="text-lg font-medium text-[var(--text-h)] mt-4 mb-2">{children}</h3>,
              p: ({ children }) => <p className="text-[var(--text)] mb-3 leading-relaxed">{children}</p>,
              ul: ({ children }) => <ul className="list-disc list-inside text-[var(--text)] mb-3 space-y-1">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-inside text-[var(--text)] mb-3 space-y-1">{children}</ol>,
              li: ({ children }) => <li className="text-[var(--text)]">{children}</li>,
              strong: ({ children }) => <strong className="font-semibold text-[var(--text-h)]">{children}</strong>,
              code: ({ children }) => <code className="bg-[var(--bg)] rounded px-1 py-0.5 text-sm">{children}</code>,
            }}
          >
            {result.cv_markdown}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}