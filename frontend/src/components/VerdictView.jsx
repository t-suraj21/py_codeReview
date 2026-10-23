import React, { useState } from 'react';
import { Award, CheckCircle2, AlertTriangle, XCircle, Copy, Check, Sparkles, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import ComplexityCard from './ComplexityCard';
import IssueList from './IssueList';

export default function VerdictView({ review, isReviewing, onTriggerReview }) {
  const [copied, setCopied] = useState(false);
  const [showCode, setShowCode] = useState(true);

  if (isReviewing) {
    return (
      <div className="glass-panel" style={{ padding: '2.5rem', textAlign: 'center' }}>
        <div style={{ position: 'relative', width: '64px', height: '64px', margin: '0 auto 1.25rem' }}>
          <Sparkles size={48} className="spin-icon" style={{ color: 'var(--accent-primary)', position: 'absolute', top: 8, left: 8 }} />
        </div>
        <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
          Analyzing with Gemini 2.5 Flash...
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '360px', margin: '0 auto' }}>
          Evaluating AST structure, calculating cyclomatic complexity, and comparing Big-O asymptotic bounds.
        </p>
      </div>
    );
  }

  if (!review) {
    return (
      <div className="glass-panel" style={{ padding: '2.5rem', textAlign: 'center' }}>
        <Sparkles size={40} style={{ color: 'var(--accent-secondary)', margin: '0 auto 1rem', display: 'block', opacity: 0.8 }} />
        <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
          Ready for AI Code Review
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '380px', margin: '0 auto 1.5rem', lineHeight: 1.5 }}>
          Submit your solution to get an intelligent assessment of code rating, algorithmic approach, time/space complexity, and optimal canonical code.
        </p>
        <button className="btn btn-primary" onClick={onTriggerReview} style={{ margin: '0 auto' }}>
          <Sparkles size={16} />
          <span>Start Review Now</span>
        </button>
      </div>
    );
  }

  const rating = review.rating ?? 0;
  const verdict = review.verdict || 'Review Complete';
  const approach = review.algorithmicApproach || review.algorithmic_approach || 'Iterative Solution';
  const optimalCode = review.correctCode || review.correct_code || '';
  const optimalExplanation = review.optimalExplanation || review.optimal_explanation || '';

  const getVerdictClass = (v) => {
    const val = v.toLowerCase();
    if (val.includes('accept')) return 'verdict-accepted';
    if (val.includes('need') || val.includes('warn')) return 'verdict-warning';
    return 'verdict-error';
  };

  const handleCopy = () => {
    if (!optimalCode) return;
    navigator.clipboard.writeText(optimalCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner: Score & Verdict */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="score-circle" style={{ '--score': rating }}>
            <div className="score-inner">
              <span className="score-num">{rating}</span>
              <span className="score-label">Rating</span>
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className={`verdict-tag ${getVerdictClass(verdict)}`}>
                {verdict}
              </span>
              <span
                style={{
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono)',
                  background: 'rgba(99, 102, 241, 0.1)',
                  color: 'var(--accent-cyan)',
                  padding: '3px 8px',
                  borderRadius: '999px',
                  border: '1px solid rgba(6, 182, 212, 0.25)'
                }}
              >
                {approach}
              </span>
            </div>
            <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', lineHeight: 1.4, maxWidth: '420px' }}>
              {review.summary}
            </p>
          </div>
        </div>
      </div>

      {/* Complexity Comparison */}
      <div>
        <h4 style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-dim)', fontWeight: 700, marginBottom: '0.5rem', letterSpacing: '0.05em' }}>
          Complexity Comparison
        </h4>
        <ComplexityCard complexity={review.complexityComparison || review.complexity_comparison} />
      </div>

      {/* Issues & Recommendations */}
      <div>
        <h4 style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-dim)', fontWeight: 700, marginBottom: '0.5rem', letterSpacing: '0.05em' }}>
          Detected Issues & Code Smells ({review.issues?.length || 0})
        </h4>
        <IssueList issues={review.issues} />
      </div>

      {/* Canonical Reference Solution */}
      {optimalCode && (
        <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
          <div
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', marginBottom: '0.5rem' }}
            onClick={() => setShowCode(!showCode)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <BookOpen size={16} style={{ color: 'var(--accent-emerald)' }} />
              <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Optimal Canonical Solution</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                className="btn btn-secondary"
                style={{ padding: '2px 8px', fontSize: '0.7rem' }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleCopy();
                }}
              >
                {copied ? <Check size={12} style={{ color: 'var(--accent-emerald)' }} /> : <Copy size={12} />}
                <span>{copied ? 'Copied!' : 'Copy'}</span>
              </button>
              {showCode ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </div>
          </div>

          {showCode && (
            <div>
              <div className="code-box">
                <pre style={{ margin: 0 }}>{optimalCode}</pre>
              </div>
              {optimalExplanation && (
                <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginTop: '0.5rem', lineHeight: 1.4, fontStyle: 'italic' }}>
                  {optimalExplanation}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
