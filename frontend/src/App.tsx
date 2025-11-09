import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import ResultsDisplay from './components/ResultsDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import ManualEntryForm from './components/ManualEntryForm';

interface TaxRecommendation {
  extracted_data: any;
  old_regime_tax: number;
  new_regime_tax: number;
  recommended_regime: string;
  savings: number;
  deductions_analysis: any;
  recommendations: string[];
  explanations: any;
  legal_references: string[];
}

function App() {
  const [activeTab, setActiveTab] = useState<'upload' | 'manual'>('manual');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<TaxRecommendation | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/analyze-form16', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze Form-16');
      }

      const data = await response.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred while processing your file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Tax Advisor</h1>
        <p className="subtitle">
          Personalized tax advisory system powered by AI
        </p>
      </header>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'manual' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('manual');
            setResults(null);
            setError(null);
          }}
        >
          Manual Entry
        </button>
        <button
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('upload');
            setResults(null);
            setError(null);
          }}
        >
          Upload Form-16
        </button>
      </div>

      <main className="App-main">
        {activeTab === 'manual' ? (
          <ManualEntryForm />
        ) : (
          <>
            {!results && !loading && (
              <FileUpload onFileUpload={handleFileUpload} />
            )}

            {loading && <LoadingSpinner />}

            {error && (
              <div className="error-message">
                <h3>Error</h3>
                <p>{error}</p>
                <button onClick={() => {
                  setError(null);
                  setResults(null);
                }}>Try Again</button>
              </div>
            )}

            {results && (
              <ResultsDisplay
                results={results}
                onReset={() => {
                  setResults(null);
                  setError(null);
                }}
              />
            )}
          </>
        )}
      </main>

      <footer className="App-footer">
        <p>Powered by Deep Learning & Large Language Models</p>
      </footer>
    </div>
  );
}

export default App;

