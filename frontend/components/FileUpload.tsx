'use client';

import React, { useState, useRef } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
  acceptedTypes: string;
}

export default function FileUpload({ onFileSelect, isProcessing, acceptedTypes }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      handleFileSelection(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      handleFileSelection(file);
    }
  };

  const handleFileSelection = (file: File) => {
    setSelectedFile(file);
    onFileSelect(file);
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full">
      {/* File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedTypes}
        onChange={handleFileChange}
        className="hidden"
        disabled={isProcessing}
      />

      {/* Drop Zone */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300'}
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-primary-400 hover:bg-gray-50'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <div className="flex flex-col items-center space-y-4">
          {/* Upload Icon */}
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
            <svg
              className="w-8 h-8 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>

          {/* Text */}
          <div>
            <p className="text-lg font-medium text-gray-900">
              {selectedFile ? 'File Selected' : 'Upload Certificate or Document'}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {selectedFile 
                ? `${selectedFile.name} (${formatFileSize(selectedFile.size)})`
                : 'Drag and drop your file here, or click to select'
              }
            </p>
          </div>

          {/* Supported formats */}
          <div className="text-xs text-gray-500">
            <p>Supported formats: PDF, PNG, JPG, JPEG, BMP, TIFF</p>
            <p>Maximum file size: 16MB</p>
          </div>

          {/* Change file button */}
          {selectedFile && !isProcessing && (
            <button
              type="button"
              className="mt-2 px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              onClick={(e) => {
                e.stopPropagation();
                openFileDialog();
              }}
            >
              Change File
            </button>
          )}
        </div>

        {/* Processing overlay */}
        {isProcessing && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
              <span className="text-primary-600 font-medium">Processing...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}