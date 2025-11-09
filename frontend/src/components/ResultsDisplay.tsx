import React from 'react';
import './ResultsDisplay.css';

interface ResultsDisplayProps {
  results: any;
  onReset: () => void;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, onReset }) => {
  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <div className="results-container">
      <div className="results-header">
        <h2>Tax Analysis Results</h2>
        <button onClick={onReset} className="reset-button">Analyze Another</button>
      </div>

      {/* Regime Comparison */}
      <div className="regime-comparison">
        <h3>Tax Regime Comparison</h3>
        <div className="regime-cards">
          <div className={`regime-card ${results.recommended_regime === 'Old Regime' ? 'recommended' : ''}`}>
            <div className="regime-header">
              <h4>Old Regime</h4>
              {results.recommended_regime === 'Old Regime' && <span className="badge">Recommended</span>}
            </div>
            <div className="tax-amount">{formatCurrency(results.old_regime_tax)}</div>
            <p className="regime-note">With deductions (80C, 80D, HRA, etc.)</p>
          </div>

          <div className={`regime-card ${results.recommended_regime === 'New Regime' ? 'recommended' : ''}`}>
            <div className="regime-header">
              <h4>New Regime</h4>
              {results.recommended_regime === 'New Regime' && <span className="badge">Recommended</span>}
            </div>
            <div className="tax-amount">{formatCurrency(results.new_regime_tax)}</div>
            <p className="regime-note">Simplified slabs, no deductions</p>
          </div>
        </div>

        <div className="savings-highlight">
          <h4>Potential Savings</h4>
          <div className="savings-amount">{formatCurrency(results.savings)}</div>
          <p>by choosing {results.recommended_regime}</p>
        </div>
      </div>

      {/* Extracted Data */}
      <div className="extracted-data">
        <h3>Extracted Information</h3>
        <div className="data-grid">
          <div className="data-item">
            <span className="data-label">Gross Salary:</span>
            <span className="data-value">{formatCurrency(results.extracted_data.gross_salary || 0)}</span>
          </div>
          <div className="data-item">
            <span className="data-label">Taxable Income:</span>
            <span className="data-value">{formatCurrency(results.extracted_data.taxable_income || 0)}</span>
          </div>
          {results.extracted_data.pan && (
            <div className="data-item">
              <span className="data-label">PAN:</span>
              <span className="data-value">{results.extracted_data.pan}</span>
            </div>
          )}
        </div>
      </div>

      {/* Deductions Analysis */}
      <div className="deductions-analysis">
        <h3>Deductions Analysis</h3>
        <div className="deductions-grid">
          <div className="deduction-item">
            <span className="deduction-label">Section 80C:</span>
            <span className="deduction-value">
              {formatCurrency(results.extracted_data.deductions?.section_80c || 0)}
            </span>
          </div>
          <div className="deduction-item">
            <span className="deduction-label">Section 80D:</span>
            <span className="deduction-value">
              {formatCurrency(results.extracted_data.deductions?.section_80d || 0)}
            </span>
          </div>
          <div className="deduction-item">
            <span className="deduction-label">Section 80CCD(1B):</span>
            <span className="deduction-value">
              {formatCurrency(results.extracted_data.deductions?.section_80ccd_1b || 0)}
            </span>
          </div>
          <div className="deduction-item">
            <span className="deduction-label">HRA:</span>
            <span className="deduction-value">
              {formatCurrency(results.extracted_data.deductions?.hra || 0)}
            </span>
          </div>
        </div>

        {results.deductions_analysis?.unclaimed_opportunities?.length > 0 && (
          <div className="unclaimed-opportunities">
            <h4>Unclaimed Deduction Opportunities</h4>
            <ul>
              {results.deductions_analysis.unclaimed_opportunities.map((opp: any, index: number) => (
                <li key={index}>
                  <strong>{opp.section}:</strong> {opp.description}
                  <br />
                  <span className="opportunity-amount">
                    Available: {formatCurrency(opp.available_amount)} | 
                    Potential Savings: {formatCurrency(opp.potential_tax_saving)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* AI Recommendations */}
      <div className="recommendations">
        <h3>AI-Powered Recommendations</h3>
        <div className="recommendations-list">
          {results.recommendations?.map((rec: string, index: number) => (
            <div key={index} className="recommendation-item">
              <span className="recommendation-icon">💡</span>
              <span className="recommendation-text">{rec}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Explanations */}
      {results.explanations && Object.keys(results.explanations).length > 0 && (
        <div className="explanations">
          <h3>Detailed Explanations</h3>
          {Object.entries(results.explanations).map(([key, value]: [string, any]) => (
            <div key={key} className="explanation-item">
              <h4>{key.replace('_', ' ').toUpperCase()}</h4>
              <p>{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Legal References */}
      {results.legal_references && results.legal_references.length > 0 && (
        <div className="legal-references">
          <h3>Legal References</h3>
          <ul>
            {results.legal_references.map((ref: string, index: number) => (
              <li key={index}>{ref}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;

