import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUpload.css';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  return (
    <div className="file-upload-container">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <div className="upload-icon">📄</div>
          {isDragActive ? (
            <p className="dropzone-text">Drop your Form-16 here...</p>
          ) : (
            <>
              <p className="dropzone-text">
                Drag & drop your Form-16 here, or click to select
              </p>
              <p className="dropzone-hint">
                Supports PDF, JPG, PNG formats
              </p>
            </>
          )}
        </div>
      </div>
      <div className="upload-info">
        <h3>How it works:</h3>
        <ul>
          <li>Upload your Form-16 document (PDF or Image)</li>
          <li>Our AI extracts all relevant tax information</li>
          <li>Get personalized recommendations for tax optimization</li>
          <li>Compare Old vs New tax regimes</li>
        </ul>
      </div>
    </div>
  );
};

export default FileUpload;

