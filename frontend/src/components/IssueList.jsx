import React from 'react';
import { AlertOctagon, AlertTriangle, Info, Check } from 'lucide-react';

export default function IssueList({ issues }) {
  if (!issues || issues.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
        <Check size={24} style={{ color: 'var(--accent-emerald)', margin: '0 auto 8px', display: 'block' }} />
        No critical issues or anti-patterns detected.
      </div>
    );
  }

  return (
    <div>
      {issues.map((issue, idx) => {
        const severity = (issue.severity || 'Info').toLowerCase();
        return (
          <div key={idx} className={`issue-card ${severity}`}>
            <div style={{ paddingTop: '2px' }}>
              {severity === 'critical' ? (
                <AlertOctagon size={16} style={{ color: 'var(--accent-rose)' }} />
              ) : severity === 'warning' ? (
                <AlertTriangle size={16} style={{ color: 'var(--accent-amber)' }} />
              ) : (
                <Info size={16} style={{ color: 'var(--accent-cyan)' }} />
              )}
            </div>

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                <span
                  style={{
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: severity === 'critical' ? '#fb7185' : severity === 'warning' ? '#fbbf24' : '#38bdf8'
                  }}
                >
                  {issue.severity || 'Issue'}
                </span>

                {issue.line && (
                  <span
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.65rem',
                      background: 'rgba(255, 255, 255, 0.05)',
                      padding: '1px 6px',
                      borderRadius: '4px',
                      color: 'var(--text-muted)'
                    }}
                  >
                    Line {issue.line}
                  </span>
                )}
              </div>

              <p style={{ fontSize: '0.825rem', color: 'var(--text-main)', margin: '2px 0 4px', lineHeight: 1.4 }}>
                {issue.message}
              </p>

              {(issue.suggestedFix || issue.suggested_fix) && (
                <div
                  style={{
                    fontSize: '0.75rem',
                    background: 'rgba(0, 0, 0, 0.25)',
                    padding: '4px 8px',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--accent-cyan)',
                    marginTop: '4px',
                    display: 'flex',
                    alignItems: 'baseline',
                    gap: '4px'
                  }}
                >
                  <strong>Fix:</strong> {issue.suggestedFix || issue.suggested_fix}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
