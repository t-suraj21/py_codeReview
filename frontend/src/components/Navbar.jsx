import React from 'react';
import { Code2, Play, Sparkles, Terminal, Activity, CheckCircle2 } from 'lucide-react';

export default function Navbar({
  language,
  setLanguage,
  selectedProblem,
  setSelectedProblem,
  problems,
  onRunTests,
  onReview,
  isRunning,
  isReviewing,
  wsConnected,
  diagnostics
}) {
  return (
    <header className="header-container">
      <div className="logo-group">
        <div className="logo-badge">
          <Code2 size={24} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 className="logo-title">PyCodeReview AI</h1>
            <span className="logo-tag">Gemini 2.5 + AST</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <span className={`status-pill ${wsConnected ? 'online' : 'error'}`}>
              <span className="pulse-dot" />
              {wsConnected ? 'Live AST Connected' : 'AST Offline'}
            </span>
            {diagnostics && diagnostics.functionCount > 0 && (
              <span style={{ color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                {diagnostics.functionCount} func | {diagnostics.loopCount} loops | complexity: {diagnostics.complexity || 1}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="nav-actions">
        {/* Problem preset selector */}
        <select
          className="select-input"
          value={selectedProblem.id}
          onChange={(e) => {
            const found = problems.find(p => p.id === e.target.value);
            if (found) setSelectedProblem(found);
          }}
        >
          {problems.map((p) => (
            <option key={p.id} value={p.id}>
              {p.title} ({p.difficulty})
            </option>
          ))}
        </select>

        {/* Language selector */}
        <select
          className="select-input"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option value="python">Python 3.13</option>
          <option value="javascript">JavaScript (Node)</option>
          <option value="cpp">C++ 17</option>
          <option value="c">C (Clang)</option>
        </select>

        {/* Run Tests button */}
        <button
          className="btn btn-secondary"
          onClick={onRunTests}
          disabled={isRunning || isReviewing}
          title="Execute code against sample test cases in sandbox"
        >
          {isRunning ? (
            <Activity size={16} className="spin-icon" />
          ) : (
            <Play size={16} style={{ color: 'var(--accent-emerald)' }} />
          )}
          <span>{isRunning ? 'Running...' : 'Run Tests'}</span>
        </button>

        {/* AI Code Review button */}
        <button
          className="btn btn-primary"
          onClick={onReview}
          disabled={isReviewing || isRunning}
          title="Perform full AI Code Review with Gemini 2.5 Flash"
        >
          <Sparkles size={16} className={isReviewing ? 'spin-icon' : ''} />
          <span>{isReviewing ? 'Analyzing...' : 'AI Code Review'}</span>
        </button>
      </div>
    </header>
  );
}
