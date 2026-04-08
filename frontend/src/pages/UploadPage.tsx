import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { FileDropzone } from '../components/upload/FileDropzone';
import { useJobStore } from '../store/jobStore';
import type { FileWithPath } from 'react-dropzone';
import { Loader2, AlertCircle, Send } from 'lucide-react';

interface UploadFormValues {
  cv_text: string;
  jd_text: string;
}

export function UploadPage() {
  const navigate = useNavigate();
  const submitJob = useJobStore((state) => state.submitJob);
  const submitError = useJobStore((state) => state.submitError);
  const [cvFiles, setCvFiles] = useState<FileWithPath[]>([]);
  const [jdFiles, setJdFiles] = useState<FileWithPath[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, watch, formState: { errors } } = useForm<UploadFormValues>({
    defaultValues: { cv_text: '', jd_text: '' },
  });

  const cvText = watch('cv_text');
  const jdText = watch('jd_text');

  const hasCv = cvFiles.length > 0 || cvText.trim().length > 0;
  const hasJd = jdFiles.length > 0 || jdText.trim().length > 0;

  const onSubmit = async (data: UploadFormValues) => {
    if (!hasCv || !hasJd) return;

    setIsSubmitting(true);
    try {
      const formData = new FormData();

      if (cvFiles.length > 0) {
        formData.append('cv_file', cvFiles[0]);
      } else if (data.cv_text.trim()) {
        formData.append('cv_text', data.cv_text.trim());
      }

      if (jdFiles.length > 0) {
        formData.append('jd_file', jdFiles[0]);
      } else if (data.jd_text.trim()) {
        formData.append('jd_text', data.jd_text.trim());
      }

      const jobId = await submitJob(formData);
      navigate(`/jobs/${jobId}`);
    } catch {
      // error shown via submitError
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl space-y-8">
        <div className="text-center space-y-2">
          <h1>Optimize Your CV</h1>
          <p className="text-[var(--text)]">
            Upload your CV and job description to get an ATS-optimized rewrite
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* CV Input */}
          <div className="space-y-4">
            <FileDropzone
              label="CV File"
              files={cvFiles}
              onFilesChange={setCvFiles}
              disabled={isSubmitting}
            />
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[var(--border)]" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-[var(--bg)] px-2 text-[var(--text)]">or paste text</span>
              </div>
            </div>
            <textarea
              {...register('cv_text')}
              placeholder="Paste your CV text here..."
              disabled={isSubmitting || cvFiles.length > 0}
              className="w-full rounded-lg border border-[var(--border)] bg-[var(--code-bg)] p-3 text-sm text-[var(--text-h)] placeholder-[var(--text)] resize-none h-32 focus:outline-none focus:border-[var(--accent)] transition-colors disabled:opacity-50"
            />
          </div>

          {/* JD Input */}
          <div className="space-y-4">
            <FileDropzone
              label="Job Description File"
              files={jdFiles}
              onFilesChange={setJdFiles}
              disabled={isSubmitting}
            />
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[var(--border)]" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-[var(--bg)] px-2 text-[var(--text)]">or paste text</span>
              </div>
            </div>
            <textarea
              {...register('jd_text')}
              placeholder="Paste the job description here..."
              disabled={isSubmitting || jdFiles.length > 0}
              className="w-full rounded-lg border border-[var(--border)] bg-[var(--code-bg)] p-3 text-sm text-[var(--text-h)] placeholder-[var(--text)] resize-none h-32 focus:outline-none focus:border-[var(--accent)] transition-colors disabled:opacity-50"
            />
          </div>

          {/* Submit Error */}
          {submitError && (
            <div className="flex items-center gap-2 rounded-lg bg-red-400/10 border border-red-400/20 p-3 text-red-400 text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{submitError}</span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!hasCv || !hasJd || isSubmitting}
            className="w-full flex items-center justify-center gap-2 rounded-lg bg-[var(--accent)] text-white py-3 font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="h-5 w-5" />
                Submit for Optimization
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}