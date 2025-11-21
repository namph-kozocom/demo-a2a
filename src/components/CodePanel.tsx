'use client';

import { 
  SandpackProvider,
  SandpackLayout,
  SandpackFileExplorer,
  SandpackCodeEditor,
  SandpackPreview
} from '@codesandbox/sandpack-react';
import { sandpackDark } from '@codesandbox/sandpack-themes';
import styles from './CodePanel.module.css';
import { useState, useEffect, useRef } from 'react';
import { Code2 } from 'lucide-react';

interface CodePanelProps {
  files: Record<string, string>;
  activeTab: 'preview' | 'code';
}

export default function CodePanel({ files, activeTab }: CodePanelProps) {
  const [sandpackFiles, setSandpackFiles] = useState<Record<string, { code: string }>>({});
  const [hasCode, setHasCode] = useState(false);
  const previousFilesRef = useRef<string>('');

  useEffect(() => {
    const hasGeneratedCode = Object.keys(files).length > 0;
    setHasCode(hasGeneratedCode);
    
    if (hasGeneratedCode) {
      // Only update if files actually changed from backend
      const currentFilesStr = JSON.stringify(files);
      if (currentFilesStr !== previousFilesRef.current) {
        previousFilesRef.current = currentFilesStr;
        
        // Convert files to Sandpack format
        const converted: Record<string, { code: string }> = {};
        Object.entries(files).forEach(([path, content]) => {
          converted[path] = { code: content };
        });
        
        setSandpackFiles(converted);
      }
    }
  }, [files]);

  return (
    <div className={styles.container}>
      {!hasCode ? (
        <div className={styles.placeholder}>
          <Code2 size={64} strokeWidth={1} />
          <h3>No Code Yet</h3>
          <p>Ask the agents to build something and watch the code appear here!</p>
          <div className={styles.examplePrompts}>
            <span>Try: "Build a todo app"</span>
            <span>Or: "Create a counter component"</span>
          </div>
        </div>
      ) : (
        <SandpackProvider
          template="react"
          theme={sandpackDark}
          files={sandpackFiles}
          customSetup={{
            dependencies: {
              'react': '^18.3.0',
              'react-dom': '^18.3.0',
            },
          }}
          options={{
            autorun: true,
            autoReload: true,
          }}
        >
          <div style={{ 
            visibility: activeTab === 'code' ? 'visible' : 'hidden',
            position: activeTab === 'code' ? 'relative' : 'absolute',
            width: '100%',
            height: '100%',
            top: 0,
            left: 0
          }}>
            <SandpackLayout>
              <SandpackFileExplorer />
              <SandpackCodeEditor 
                showLineNumbers
                showInlineErrors
                wrapContent
              />
            </SandpackLayout>
          </div>
          <div style={{ 
            visibility: activeTab === 'preview' ? 'visible' : 'hidden',
            position: activeTab === 'preview' ? 'relative' : 'absolute',
            width: '100%',
            height: '100%',
            top: 0,
            left: 0
          }}>
            <SandpackLayout>
              <SandpackPreview 
                showNavigator={false}
              />
            </SandpackLayout>
          </div>
        </SandpackProvider>
      )}
    </div>
  );
}
