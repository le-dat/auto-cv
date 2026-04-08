import { FileUp } from 'lucide-react';
import { Link } from 'react-router-dom';

export function Header() {
  return (
    <header className="border-b border-[var(--border)] bg-[var(--bg)]">
      <div className="mx-auto max-w-7xl px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <FileUp className="h-6 w-6 text-[var(--accent)]" />
          <span className="text-lg font-semibold text-[var(--text-h)]">CV Optimizer</span>
        </Link>
        <nav className="flex items-center gap-6">
          <Link
            to="/"
            className="text-sm text-[var(--text)] hover:text-[var(--text-h)] transition-colors"
          >
            Upload
          </Link>
          <span className="text-xs text-[var(--text)] opacity-60">AI-powered CV rewriting</span>
        </nav>
      </div>
    </header>
  );
}