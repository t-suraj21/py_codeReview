import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import Navbar from './components/Navbar';
import CodeEditor from './components/CodeEditor';
import TestCaseRunner from './components/TestCaseRunner';
import VerdictView from './components/VerdictView';
import { PROBLEMS } from './data/problems';
import { useWebSocket } from './hooks/useWebSocket';
import { apiService } from './services/api';
import { AlertCircle, HelpCircle } from 'lucide-react';

export default function App() {
  const [selectedProblem, setSelectedProblem] = useState(PROBLEMS[0]);
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState(selectedProblem.defaultCodes.python || '');
  const [testCases, setTestCases] = useState(selectedProblem.testCases || []);
  const [testResults, setTestResults] = useState(null);
  const [review, setReview] = useState(null);

  const [isRunning, setIsRunning] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);
  const [customOutput, setCustomOutput] = useState('');
  const [customError, setCustomError] = useState('');
  const [notification, setNotification] = useState(null);

  // Real-time AST Diagnostics via WebSocket
  const { isConnected: wsConnected, diagnostics } = useWebSocket(code, language);

  // Sync problem code when problem or language changes
  useEffect(() => {
    const defaultCode = selectedProblem.defaultCodes[language] || selectedProblem.defaultCodes.python || '';
    setCode(defaultCode);
    setTestCases(selectedProblem.testCases || []);
    setTestResults(null);
    setReview(null);
    setCustomOutput('');
    setCustomError('');
  }, [selectedProblem, language]);

  // Trigger celebration confetti
  const triggerConfetti = () => {
    try {
      confetti({
        particleCount: 80,
        spread: 60,
        origin: { y: 0.6 }
      });
    } catch (e) {
      // ignore
    }
  };

  // Run Batch Tests
  const handleRunTests = async () => {
    setIsRunning(true);
    setNotification(null);
    try {
      const data = await apiService.runBatchTests({
        code,
        language,
        testCases
      });
      setTestResults(data.results);
      if (data.totalPassed === data.totalCases && data.totalCases > 0) {
        setNotification({ type: 'success', message: `All ${data.totalCases} test cases passed!` });
      } else {
        setNotification({ type: 'warning', message: `${data.totalPassed}/${data.totalCases} test cases passed.` });
      }
    } catch (err) {
      console.error('Run tests error:', err);
      setNotification({ type: 'error', message: `Execution failed: ${err.message}` });
    } finally {
      setIsRunning(false);
    }
  };

  // Run Custom Input
  const handleRunSingle = async (inputStr) => {
    setIsRunning(true);
    setCustomOutput('');
    setCustomError('');
    try {
      const data = await apiService.runSingle({
        code,
        language,
        input: inputStr
      });
      setCustomOutput(data.stdout);
      setCustomError(data.stderr);
    } catch (err) {
      setCustomError(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  // Run AI Code Review
  const handleReview = async () => {
    setIsReviewing(true);
    setNotification(null);
    try {
      const data = await apiService.submitReview({
        code,
        language,
        problemTitle: selectedProblem.title,
        problemDescription: selectedProblem.description,
        testCases
      });
      setReview(data);
      if (data.testCaseResults && data.testCaseResults.length > 0) {
        setTestResults(data.testCaseResults);
      }
      if (data.rating >= 90 && data.verdict?.toLowerCase().includes('accept')) {
        triggerConfetti();
      }
    } catch (err) {
      console.error('Code review error:', err);
      setNotification({ type: 'error', message: `AI Review failed: ${err.message}` });
    } finally {
      setIsReviewing(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar */}
      <Navbar
        language={language}
        setLanguage={setLanguage}
        selectedProblem={selectedProblem}
        setSelectedProblem={setSelectedProblem}
        problems={PROBLEMS}
        onRunTests={handleRunTests}
        onReview={handleReview}
        isRunning={isRunning}
        isReviewing={isReviewing}
        wsConnected={wsConnected}
        diagnostics={diagnostics}
      />

      {/* Optional Notification Toast */}
      {notification && (
        <div
          style={{
            padding: '0.4rem 1rem',
            fontSize: '0.8rem',
            textAlign: 'center',
            background: notification.type === 'success' ? 'rgba(16, 185, 129, 0.2)' : notification.type === 'warning' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(244, 63, 94, 0.2)',
            color: notification.type === 'success' ? '#34d399' : notification.type === 'warning' ? '#fbbf24' : '#fb7185',
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)'
          }}
        >
          {notification.message}
        </div>
      )}

      {/* Main Workspace */}
      <main className="workspace-grid">
        {/* Left Column: Editor & Test Cases */}
        <section className="editor-pane">
          {/* Problem Brief Card */}
          <div className="glass-panel" style={{ padding: '0.75rem 1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h2 style={{ fontSize: '1rem', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
                {selectedProblem.title}
              </h2>
              <span
                style={{
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  padding: '2px 8px',
                  borderRadius: '999px',
                  background: selectedProblem.difficulty === 'Easy' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                  color: selectedProblem.difficulty === 'Easy' ? '#34d399' : '#fbbf24'
                }}
              >
                {selectedProblem.difficulty}
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px', lineHeight: 1.4 }}>
              {selectedProblem.description}
            </p>
          </div>

          {/* Monaco Editor */}
          <CodeEditor
            code={code}
            setCode={setCode}
            language={language}
            diagnostics={diagnostics}
          />

          {/* Test Case Runner Panel */}
          <TestCaseRunner
            testCases={testCases}
            setTestCases={setTestCases}
            testResults={testResults}
            isRunning={isRunning}
            onRunSingle={handleRunSingle}
            customOutput={customOutput}
            customError={customError}
          />
        </section>

        {/* Right Column: AI Review & Verdict Dashboard */}
        <aside className="analysis-pane">
          <VerdictView
            review={review}
            isReviewing={isReviewing}
            onTriggerReview={handleReview}
          />
        </aside>
      </main>
    </div>
  );
}
