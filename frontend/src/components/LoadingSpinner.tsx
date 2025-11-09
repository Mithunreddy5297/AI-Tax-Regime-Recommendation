import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner: React.FC = () => {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p className="loading-text">Analyzing your Form-16...</p>
      <p className="loading-subtext">This may take a few moments</p>
    </div>
  );
};

export default LoadingSpinner;

