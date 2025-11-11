import React, { useState, useEffect, useCallback } from 'react';
import './ManualEntryForm.css';
import axios from 'axios';

interface TaxCalculation {
  old_regime_tax: number;
  new_regime_tax: number;
  recommended_regime: string;
  savings: number;
  taxable_income_old: number;
  taxable_income_new: number;
  total_deductions: number;
  deductions_analysis: any;
  tax_breakdown: any;
}

const ManualEntryForm: React.FC = () => {
  const [formData, setFormData] = useState({
    age_group: 'below_60',
    gross_salary: '',
    deductions: {
      section_80c: '',
      section_80d: '',
      section_80ccd_1b: '',
      section_80tta: '',
      section_80ttb: '',
      section_24b: '',
      hra_basic_salary: '',
      hra_received: '',
      rent_paid: '',
      is_metro: false,
      section_80g: '',
      section_80e: '',
      section_80ee: '',
      section_80gg: '',
      other_deductions: ''
    }
  });

  const [taxCalculation, setTaxCalculation] = useState<TaxCalculation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Debounce function for real-time calculation
  const debounce = useCallback((func: Function, wait: number) => {
    let timeout: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  }, []);

  // Calculate tax in real-time
  const calculateTax = useCallback(async () => {
    const grossSalary = parseFloat(formData.gross_salary) || 0;
    
    if (grossSalary === 0) {
      setTaxCalculation(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const deductions: any = {};
      Object.keys(formData.deductions).forEach(key => {
        const value = formData.deductions[key as keyof typeof formData.deductions];
        
        // Handle boolean (is_metro)
        if (key === 'is_metro') {
          deductions[key] = value === true || value === 'true';
        } else {
          // Handle numeric values
          const numValue = parseFloat(value as string) || 0;
          if (numValue > 0) {
            deductions[key] = numValue;
          }
        }
      });

      const response = await axios.post('/api/calculate-tax-realtime', {
        age_group: formData.age_group,
        gross_salary: grossSalary,
        deductions: deductions
      });

      setTaxCalculation(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error calculating tax');
      setTaxCalculation(null);
    } finally {
      setLoading(false);
    }
  }, [formData]);

  // Debounced calculation
  const debouncedCalculate = useCallback(
    debounce(calculateTax, 500),
    [formData, debounce]
  );

  useEffect(() => {
    debouncedCalculate();
  }, [formData, debouncedCalculate]);

  const handleInputChange = (field: string, value: string | boolean) => {
    if (field === 'age_group' || field === 'gross_salary') {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        deductions: {
          ...prev.deductions,
          [field]: value
        }
      }));
    }
  };

  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <div className="manual-entry-container">
      <div className="form-section">
        <h2>AI Tax Advisor</h2>
        <p className="subtitle">Enter your details to calculate tax & get personalized AI advice</p>

        <div className="form-grid">
          {/* Basic Information */}
          <div className="form-group">
            <label>Age Group</label>
            <select
              value={formData.age_group}
              onChange={(e) => handleInputChange('age_group', e.target.value)}
              className="form-input"
            >
              <option value="below_60">Below 60 years</option>
              <option value="60_80">60-80 years (Senior Citizen)</option>
              <option value="above_80">Above 80 years (Super Senior Citizen)</option>
            </select>
          </div>

          {/* Income Details */}
          <div className="form-group full-width">
            <label>Gross Annual Salary</label>
            <input
              type="number"
              value={formData.gross_salary}
              onChange={(e) => handleInputChange('gross_salary', e.target.value)}
              placeholder="e.g., 1500000"
              className="form-input"
            />
            <p className="form-note">Standard Deduction of ₹50,000 is auto-applied.</p>
          </div>

          {/* Common Deductions */}
          <div className="form-group full-width">
            <h3>Common Deductions (Old Regime)</h3>
          </div>

          <div className="form-group">
            <label>Section 80C</label>
            <input
              type="number"
              value={formData.deductions.section_80c}
              onChange={(e) => handleInputChange('section_80c', e.target.value)}
              placeholder="e.g., 150000"
              className="form-input"
            />
            <span className="form-hint">Max: ₹1,50,000</span>
          </div>

          <div className="form-group">
            <label>NPS Contribution 80CCD(1B)</label>
            <input
              type="number"
              value={formData.deductions.section_80ccd_1b}
              onChange={(e) => handleInputChange('section_80ccd_1b', e.target.value)}
              placeholder="e.g., 50000"
              className="form-input"
            />
            <span className="form-hint">Max: ₹50,000</span>
          </div>

          <div className="form-group">
            <label>Interest from Savings - 80TTA/80TTB</label>
            <input
              type="number"
              value={
                formData.age_group === '60_80' || formData.age_group === 'above_80'
                  ? formData.deductions.section_80ttb
                  : formData.deductions.section_80tta
              }
              onChange={(e) => {
                const ageGroup = formData.age_group;
                if (ageGroup === '60_80' || ageGroup === 'above_80') {
                  handleInputChange('section_80ttb', e.target.value);
                  // Clear 80TTA when using 80TTB
                  if (e.target.value) {
                    handleInputChange('section_80tta', '');
                  }
                } else {
                  handleInputChange('section_80tta', e.target.value);
                  // Clear 80TTB when using 80TTA
                  if (e.target.value) {
                    handleInputChange('section_80ttb', '');
                  }
                }
              }}
              placeholder="e.g., 5000"
              className="form-input"
            />
            <span className="form-hint">
              {formData.age_group === '60_80' || formData.age_group === 'above_80' 
                ? 'Max: ₹50,000 (80TTB)' 
                : 'Max: ₹10,000 (80TTA)'}
            </span>
          </div>

          <div className="form-group">
            <label>Section 80D - Medical Insurance</label>
            <input
              type="number"
              value={formData.deductions.section_80d}
              onChange={(e) => handleInputChange('section_80d', e.target.value)}
              placeholder="e.g., 20000"
              className="form-input"
            />
            <span className="form-hint">
              Max: ₹{formData.age_group === '60_80' || formData.age_group === 'above_80' ? '50,000' : '25,000'}
            </span>
          </div>

          <div className="form-group">
            <label>Home Loan Interest - Sec 24(b)</label>
            <input
              type="number"
              value={formData.deductions.section_24b}
              onChange={(e) => handleInputChange('section_24b', e.target.value)}
              placeholder="e.g., 200000"
              className="form-input"
            />
            <span className="form-hint">Max: ₹2,00,000</span>
          </div>

          {/* HRA Section */}
          <div className="form-group full-width">
            <h3>House Rent Allowance (HRA)</h3>
          </div>

          <div className="form-group">
            <label>Annual Basic Salary</label>
            <input
              type="number"
              value={formData.deductions.hra_basic_salary}
              onChange={(e) => handleInputChange('hra_basic_salary', e.target.value)}
              placeholder="e.g., 600000"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Total Rent Paid</label>
            <input
              type="number"
              value={formData.deductions.rent_paid}
              onChange={(e) => handleInputChange('rent_paid', e.target.value)}
              placeholder="e.g., 240000"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Total HRA Received</label>
            <input
              type="number"
              value={formData.deductions.hra_received}
              onChange={(e) => handleInputChange('hra_received', e.target.value)}
              placeholder="e.g., 200000"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.deductions.is_metro}
                onChange={(e) => handleInputChange('is_metro', e.target.checked)}
                style={{ width: 'auto', cursor: 'pointer' }}
              />
              <span>I live in a metro city</span>
            </label>
            <span className="form-hint">Metro cities: Delhi, Mumbai, Chennai, Kolkata</span>
          </div>

          <div className="form-group">
            <label>Section 80G - Donations</label>
            <input
              type="number"
              value={formData.deductions.section_80g}
              onChange={(e) => handleInputChange('section_80g', e.target.value)}
              placeholder="e.g., 10000"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Other Deductions</label>
            <input
              type="number"
              value={formData.deductions.other_deductions}
              onChange={(e) => handleInputChange('other_deductions', e.target.value)}
              placeholder="e.g., 0"
              className="form-input"
            />
          </div>

          {/* Advanced Deductions */}
          <div className="form-group full-width">
            <button
              type="button"
              className="advanced-toggle"
              onClick={() => setShowAdvanced(!showAdvanced)}
              style={{
                background: 'none',
                border: '1px solid #007bff',
                color: '#007bff',
                padding: '10px 15px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.95rem',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}
            >
              {showAdvanced ? '▼' : '▶'} Advanced Deductions (Optional)
            </button>
          </div>

          {showAdvanced && (
            <>
              <div className="form-group full-width" style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid #ddd' }}>
                <h3 style={{ color: '#555', marginBottom: '15px' }}>Advanced Deductions</h3>
              </div>

              <div className="form-group">
                <label>Section 80E - Education Loan Interest</label>
                <input
                  type="number"
                  value={formData.deductions.section_80e}
                  onChange={(e) => handleInputChange('section_80e', e.target.value)}
                  placeholder="e.g., 50000"
                  className="form-input"
                />
                <span className="form-hint">No upper limit - entire interest paid</span>
              </div>

              <div className="form-group">
                <label>Section 80EE - First-time Homebuyer</label>
                <input
                  type="number"
                  value={formData.deductions.section_80ee}
                  onChange={(e) => handleInputChange('section_80ee', e.target.value)}
                  placeholder="e.g., 150000"
                  className="form-input"
                />
                <span className="form-hint">Max: ₹1,50,000 (in addition to 24B)</span>
              </div>

              <div className="form-group">
                <label>Section 80GG - Rent Deduction (Without HRA)</label>
                <input
                  type="number"
                  value={formData.deductions.section_80gg}
                  onChange={(e) => handleInputChange('section_80gg', e.target.value)}
                  placeholder="e.g., 60000"
                  className="form-input"
                />
                <span className="form-hint">Use only if NOT claiming HRA - Max: ₹5,000/month</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Real-time Tax Calculation Results */}
      {loading && (
        <div className="calculation-loading">
          <div className="spinner-small"></div>
          <p>Calculating...</p>
        </div>
      )}

      {error && (
        <div className="error-box">
          <p>{error}</p>
        </div>
      )}

      {taxCalculation && !loading && (
        <div className="tax-results">
          <h3>Tax Calculation Results</h3>
          
          <div className="regime-comparison-cards">
            <div className={`regime-card ${taxCalculation.recommended_regime === 'Old Regime' ? 'recommended' : ''}`}>
              <div className="regime-header">
                <h4>Old Regime</h4>
                {taxCalculation.recommended_regime === 'Old Regime' && <span className="badge">Recommended</span>}
              </div>
              <div className="tax-amount">{formatCurrency(taxCalculation.old_regime_tax)}</div>
              <div className="tax-details">
                <p>Taxable Income: {formatCurrency(taxCalculation.taxable_income_old)}</p>
                <p>Total Deductions: {formatCurrency(taxCalculation.total_deductions)}</p>
              </div>
            </div>

            <div className={`regime-card ${taxCalculation.recommended_regime === 'New Regime' ? 'recommended' : ''}`}>
              <div className="regime-header">
                <h4>New Regime</h4>
                {taxCalculation.recommended_regime === 'New Regime' && <span className="badge">Recommended</span>}
              </div>
              <div className="tax-amount">{formatCurrency(taxCalculation.new_regime_tax)}</div>
              <div className="tax-details">
                <p>Taxable Income: {formatCurrency(taxCalculation.taxable_income_new)}</p>
                <p>Standard Deduction: ₹50,000</p>
              </div>
            </div>
          </div>

          <div className="savings-highlight">
            <h4>Potential Savings</h4>
            <div className="savings-amount">{formatCurrency(taxCalculation.savings)}</div>
            <p>by choosing {taxCalculation.recommended_regime}</p>
          </div>

          {taxCalculation.deductions_analysis?.unclaimed_opportunities?.length > 0 && (
            <div className="unclaimed-section">
              <h4>Unclaimed Deduction Opportunities</h4>
              <ul>
                {taxCalculation.deductions_analysis.unclaimed_opportunities.map((opp: any, index: number) => (
                  <li key={index}>
                    <strong>{opp.section}:</strong> {opp.description}
                    <br />
                    <span className="opportunity-detail">
                      Available: {formatCurrency(opp.available_amount)} | 
                      Potential Savings: {formatCurrency(opp.potential_tax_saving)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ManualEntryForm;

