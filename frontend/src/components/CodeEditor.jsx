import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { Terminal, AlertCircle, FileCode } from 'lucide-react';

export default function CodeEditor({ code, setCode, language, diagnostics }) {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Configure editor defaults
    editor.updateOptions({
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      fontSize: 14,
      lineHeight: 22,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      smoothScrolling: true,
      cursorBlinking: 'smooth',
      renderWhitespace: 'selection',
      padding: { top: 12, bottom: 12 }
    });
  };

  // Sync AST diagnostics to Monaco markers
  useEffect(() => {
    if (!editorRef.current || !monacoRef.current) return;
    const model = editorRef.current.getModel();
    if (!model) return;

    if (diagnostics && diagnostics.markers) {
      monacoRef.current.editor.setModelMarkers(model, 'pycode_ast_diagnostics', diagnostics.markers);
    } else {
      monacoRef.current.editor.setModelMarkers(model, 'pycode_ast_diagnostics', []);
    }
  }, [diagnostics]);

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: '360px', overflow: 'hidden' }}>
      <div className="pane-header">
        <div className="pane-title">
          <FileCode size={16} style={{ color: 'var(--accent-primary)' }} />
          <span>Solution Editor</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
            ({language})
          </span>
        </div>

        {diagnostics?.hasError && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--accent-rose)' }}>
            <AlertCircle size={14} />
            <span>Syntax Warning: Line {diagnostics.markers?.[0]?.startLineNumber || 1}</span>
          </div>
        )}
      </div>

      <div style={{ flex: 1, position: 'relative' }}>
        <Editor
          height="100%"
          language={language === 'c' || language === 'cpp' ? 'cpp' : language}
          value={code}
          onChange={(newVal) => setCode(newVal || '')}
          theme="vs-dark"
          onMount={handleEditorDidMount}
          options={{
            automaticLayout: true,
            tabSize: 4,
          }}
        />
      </div>
    </div>
  );
}
