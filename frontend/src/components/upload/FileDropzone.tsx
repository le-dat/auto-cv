import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X } from 'lucide-react';
import type { FileWithPath } from 'react-dropzone';

interface FileDropzoneProps {
  label: string;
  accept?: Record<string, string[]>;
  files: FileWithPath[];
  onFilesChange: (files: FileWithPath[]) => void;
  disabled?: boolean;
}

export function FileDropzone({
  label,
  accept = { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'], 'text/plain': ['.txt'] },
  files,
  onFilesChange,
  disabled = false,
}: FileDropzoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: FileWithPath[]) => {
      if (files.length === 0) {
        onFilesChange(acceptedFiles);
      }
    },
    [files, onFilesChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxFiles: 1,
    disabled: disabled || files.length > 0,
  });

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFilesChange([]);
  };

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-[var(--text-h)]">{label}</label>
      <div
        {...getRootProps()}
        className={`
          relative cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-all
          ${isDragActive ? 'border-[var(--accent)] bg-[var(--accent-bg)]' : 'border-[var(--border)] hover:border-[var(--accent)]'}
          ${disabled || files.length > 0 ? 'cursor-default opacity-60' : ''}
        `}
      >
        <input {...getInputProps()} />
        {files.length > 0 ? (
          <div className="flex items-center justify-center gap-3">
            <FileText className="h-8 w-8 text-[var(--accent)]" />
            <div className="text-left">
              <p className="text-sm font-medium text-[var(--text-h)]">{files[0].name}</p>
              <p className="text-xs text-[var(--text)]">{(files[0].size / 1024).toFixed(1)} KB</p>
            </div>
            {!disabled && (
              <button
                type="button"
                onClick={removeFile}
                className="ml-4 rounded-full p-1 hover:bg-[var(--social-bg)] transition-colors"
              >
                <X className="h-4 w-4 text-[var(--text)]" />
              </button>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className={`h-10 w-10 ${isDragActive ? 'text-[var(--accent)]' : 'text-[var(--text)]'}`} />
            <p className="text-sm text-[var(--text)]">
              {isDragActive ? 'Drop the file here' : 'Drag & drop or click to upload'}
            </p>
            <p className="text-xs text-[var(--text)] opacity-60">PDF, DOCX, TXT</p>
          </div>
        )}
      </div>
    </div>
  );
}