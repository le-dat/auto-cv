import type { MatchResult } from '../../types/api';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface ScoreDisplayProps {
  matchResult: MatchResult;
}

export function ScoreDisplay({ matchResult }: ScoreDisplayProps) {
  const { score, matching_skills, missing_skills, strong_skills, suggestions, ats_keywords } = matchResult;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-400/10 border-green-400/20';
    if (score >= 60) return 'bg-yellow-400/10 border-yellow-400/20';
    return 'bg-red-400/10 border-red-400/20';
  };

  return (
    <div className="space-y-6">
      {/* Score */}
      <div className={`rounded-lg border p-6 text-center ${getScoreBg(score)}`}>
        <p className="text-sm font-medium text-[var(--text)] mb-2">Match Score</p>
        <p className={`text-5xl font-bold ${getScoreColor(score)}`}>{score.toFixed(1)}%</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Strong Skills */}
        <div className="rounded-lg border border-[var(--border)] bg-[var(--code-bg)] p-4">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="h-5 w-5 text-green-400" />
            <h3 className="font-medium text-[var(--text-h)]">Strong Skills</h3>
          </div>
          <ul className="space-y-1">
            {strong_skills.map((skill) => (
              <li key={skill} className="text-sm text-[var(--text)]">• {skill}</li>
            ))}
          </ul>
        </div>

        {/* Missing Skills */}
        <div className="rounded-lg border border-[var(--border)] bg-[var(--code-bg)] p-4">
          <div className="flex items-center gap-2 mb-3">
            <XCircle className="h-5 w-5 text-red-400" />
            <h3 className="font-medium text-[var(--text-h)]">Missing Skills</h3>
          </div>
          <ul className="space-y-1">
            {missing_skills.map((skill) => (
              <li key={skill} className="text-sm text-[var(--text)]">• {skill}</li>
            ))}
          </ul>
        </div>

        {/* Matching Skills */}
        <div className="rounded-lg border border-[var(--border)] bg-[var(--code-bg)] p-4">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="h-5 w-5 text-[var(--accent)]" />
            <h3 className="font-medium text-[var(--text-h)]">Matching Skills</h3>
          </div>
          <ul className="space-y-1">
            {matching_skills.map((skill) => (
              <li key={skill} className="text-sm text-[var(--text)]">• {skill}</li>
            ))}
          </ul>
        </div>

        {/* Suggestions */}
        <div className="rounded-lg border border-[var(--border)] bg-[var(--code-bg)] p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="h-5 w-5 text-yellow-400" />
            <h3 className="font-medium text-[var(--text-h)]">Suggestions</h3>
          </div>
          <ul className="space-y-1">
            {suggestions.map((s) => (
              <li key={s} className="text-sm text-[var(--text)]">• {s}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* ATS Keywords */}
      {ats_keywords.length > 0 && (
        <div className="rounded-lg border border-[var(--border)] bg-[var(--code-bg)] p-4">
          <h3 className="font-medium text-[var(--text-h)] mb-3">ATS Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {ats_keywords.map((kw) => (
              <span
                key={kw}
                className="rounded-full bg-[var(--accent-bg)] px-3 py-1 text-xs text-[var(--accent)] border border-[var(--accent-border)]"
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}