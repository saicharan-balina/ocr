'use client';

import React from 'react';
import { OCRResult } from '../lib/api';

interface ResultDisplayProps {
  result: OCRResult;
  onReset: () => void;
}

export default function ResultDisplay({ result, onReset }: ResultDisplayProps) {
  const copyToClipboard = async () => {
    if (result.text) {
      await navigator.clipboard.writeText(result.text);
      // You could add a toast notification here
      alert('Text copied to clipboard!');
    }
  };

  const downloadText = () => {
    if (result.text) {
      const element = document.createElement('a');
      const file = new Blob([result.text], { type: 'text/plain' });
      element.href = URL.createObjectURL(file);
      element.download = `extracted-text-${Date.now()}.txt`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
  };

  if (!result.success) {
    return (
      <div className="w-full max-w-4xl bg-white rounded-lg shadow-lg p-6">
        {/* Error Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-red-800">Processing Failed</h2>
          </div>
          <button
            onClick={onReset}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Try Again
          </button>
        </div>

        {/* Error Message */}
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{result.error || result.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl bg-white rounded-lg shadow-lg p-6">
      {/* Success Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-green-800">Text Extracted Successfully</h2>
        </div>
        <button
          onClick={onReset}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          Process Another File
        </button>
      </div>

      {/* File Info */}
      <div className="bg-gray-50 rounded-md p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">File:</span>
            <p className="text-gray-600 truncate">{result.original_filename}</p>
          </div>
          <div>
            <span className="font-medium text-gray-700">Type:</span>
            <p className="text-gray-600 capitalize">{result.file_type}</p>
          </div>
          <div>
            <span className="font-medium text-gray-700">Pages:</span>
            <p className="text-gray-600">{result.pages}</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={copyToClipboard}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <span>Copy Text</span>
        </button>
        <button
          onClick={downloadText}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>Download</span>
        </button>
      </div>

      {/* Extracted Text */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Extracted Text</h3>
        
        {result.file_type === 'pdf' && result.page_texts ? (
          // PDF with multiple pages
          <div className="space-y-4">
            {result.page_texts.map((pageText, index) => (
              <div key={index} className="border border-gray-200 rounded-md">
                <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                  <h4 className="font-medium text-gray-700">Page {index + 1}</h4>
                </div>
                <textarea
                  value={pageText}
                  readOnly
                  className="w-full p-4 min-h-[200px] resize-none border-none focus:ring-0 text-sm font-mono"
                  placeholder={pageText.trim() === '' ? 'No text found on this page' : undefined}
                />
              </div>
            ))}
          </div>
        ) : (
          // Single page or image
          <textarea
            value={result.text}
            readOnly
            className="w-full p-4 min-h-[300px] border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm font-mono"
            placeholder={result.text?.trim() === '' ? 'No text found in the document' : undefined}
          />
        )}
      </div>

      {/* Character Count */}
      <div className="mt-4 text-sm text-gray-500">
        Total characters: {result.text?.length || 0}
      </div>
    </div>
  );
}