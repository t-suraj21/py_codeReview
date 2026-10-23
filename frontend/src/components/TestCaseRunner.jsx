import React, { useState } from 'react';
import { Play, CheckCircle2, XCircle, Clock, Plus, Terminal, AlertTriangle } from 'lucide-react';

export default function TestCaseRunner({
  testCases,
  setTestCases,
  testResults,
  isRunning,
  onRunSingle,
  customOutput,
  customError
}) {
  const [activeTab, setActiveTab] = useState('cases'); // 'cases' | 'custom'
  const [selectedCaseIdx, setSelectedCaseIdx] = useState(0);
  const [customInput, setCustomInput] = useState('');

  const addTestCase = () => {
    setTestCases([
      ...testCases,
      { input: '', expectedOutput: '' }
    ]);
    setSelectedCaseIdx(testCases.length);
  };

  const updateTestCase = (idx, field, value) => {
    const updated = [...testCases];
    updated[idx] = { ...updated[idx], [field]: value };
    setTestCases(updated);
  };

  const currentResult = testResults && testResults[selectedCaseIdx];

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '240px', overflow: 'hidden' }}>
      <div className="pane-header" style={{ padding: '0.5rem 1rem' }}>
        <div className="tabs-container">
          <button
            className={`tab-btn ${activeTab === 'cases' ? 'active' : ''}`}
            onClick={() => setActiveTab('cases')}
          >
            Test Cases ({testCases.length})
          </button>
          <button
            className={`tab-btn ${activeTab === 'custom' ? 'active' : ''}`}
            onClick={() => setActiveTab('custom')}
          >
            Custom Input
          </button>
        </div>

        {activeTab === 'cases' && (
          <button
            className="btn btn-secondary"
            style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
            onClick={addTestCase}
          >
            <Plus size={14} />
            <span>Add Case</span>
          </button>
        )}
      </div>

      <div style={{ flex: 1, padding: '0.75rem 1rem', overflowY: 'auto' }}>
        {activeTab === 'cases' ? (
          <div>
            {/* Case selector pills */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', overflowX: 'auto', paddingBottom: '4px' }}>
              {testCases.map((tc, idx) => {
                const res = testResults && testResults[idx];
                return (
                  <button
                    key={idx}
                    onClick={() => setSelectedCaseIdx(idx)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '4px 10px',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.75rem',
                      fontFamily: 'var(--font-mono)',
                      background: selectedCaseIdx === idx ? 'var(--bg-tertiary)' : 'rgba(255, 255, 255, 0.03)',
                      color: selectedCaseIdx === idx ? 'var(--text-main)' : 'var(--text-muted)',
                      border: selectedCaseIdx === idx ? '1px solid var(--accent-primary)' : '1px solid var(--border-glass)',
                      cursor: 'pointer'
                    }}
                  >
                    {res ? (
                      res.passed ? (
                        <CheckCircle2 size={12} style={{ color: 'var(--accent-emerald)' }} />
                      ) : (
                        <XCircle size={12} style={{ color: 'var(--accent-rose)' }} />
                      )
                    ) : (
                      <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--text-dim)' }} />
                    )}
                    <span>Case {idx + 1}</span>
                  </button>
                );
              })}
            </div>

            {/* Selected case editor and result */}
            {testCases[selectedCaseIdx] && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                    Input
                  </label>
                  <textarea
                    rows={2}
                    className="select-input"
                    style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', resize: 'none', marginTop: '4px' }}
                    value={testCases[selectedCaseIdx].input}
                    onChange={(e) => updateTestCase(selectedCaseIdx, 'input', e.target.value)}
                    placeholder="e.g. [2,7,11,15]\n9"
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                    Expected Output
                  </label>
                  <textarea
                    rows={2}
                    className="select-input"
                    style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', resize: 'none', marginTop: '4px' }}
                    value={testCases[selectedCaseIdx].expectedOutput}
                    onChange={(e) => updateTestCase(selectedCaseIdx, 'expectedOutput', e.target.value)}
                    placeholder="e.g. [0, 1]"
                  />
                </div>
              </div>
            )}

            {/* Result banner */}
            {currentResult && (
              <div
                style={{
                  marginTop: '0.75rem',
                  padding: '0.5rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.75rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: currentResult.passed ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
                  border: `1px solid ${currentResult.passed ? 'rgba(16, 185, 129, 0.25)' : 'rgba(244, 63, 94, 0.25)'}`
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {currentResult.passed ? (
                    <CheckCircle2 size={14} style={{ color: 'var(--accent-emerald)' }} />
                  ) : (
                    <XCircle size={14} style={{ color: 'var(--accent-rose)' }} />
                  )}
                  <span style={{ fontWeight: 600, color: currentResult.passed ? '#34d399' : '#fb7185' }}>
                    {currentResult.passed ? 'Passed' : 'Failed'}
                  </span>
                  <span style={{ color: 'var(--text-muted)' }}>— {currentResult.explanation}</span>
                </div>

                {currentResult.executionTimeMs && (
                  <span style={{ color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    {currentResult.executionTimeMs} ms
                  </span>
                )}
              </div>
            )}
          </div>
        ) : (
          <div>
            <div style={{ display: 'flex', gap: '0.75rem', height: '100%' }}>
              <div style={{ flex: 1 }}>
                <textarea
                  rows={4}
                  className="select-input"
                  style={{ width: '100%', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', resize: 'none' }}
                  value={customInput}
                  onChange={(e) => setCustomInput(e.target.value)}
                  placeholder="Enter custom stdin input here..."
                />
                <button
                  className="btn btn-secondary"
                  style={{ marginTop: '0.4rem', padding: '0.35rem 0.8rem', fontSize: '0.75rem' }}
                  onClick={() => onRunSingle(customInput)}
                  disabled={isRunning}
                >
                  <Play size={12} />
                  <span>Execute Custom Input</span>
                </button>
              </div>

              <div style={{ flex: 1 }}>
                <div className="code-box" style={{ height: '110px', fontSize: '0.75rem' }}>
                  {customOutput ? (
                    <pre style={{ margin: 0 }}>{customOutput}</pre>
                  ) : customError ? (
                    <pre style={{ margin: 0, color: 'var(--accent-rose)' }}>{customError}</pre>
                  ) : (
                    <span style={{ color: 'var(--text-dim)' }}>Output will appear here...</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
