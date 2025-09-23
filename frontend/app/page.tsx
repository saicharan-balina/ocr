'use client';

import React, { useState, useEffect } from 'react';
import FileUpload from '../components/FileUpload';
import ResultDisplay from '../components/ResultDisplay';
import { ocrApi, OCRResult } from '../lib/api';

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<OCRResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Check backend status on component mount
  useEffect(() => {
    checkBackendStatus();
  }, []);

  const checkBackendStatus = async () => {
    try {
      await ocrApi.healthCheck();
      setBackendStatus('online');
    } catch (error) {
      setBackendStatus('offline');
    }
  };

  const handleFileSelect = async (file: File) => {
    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const ocrResult = await ocrApi.processFile(file);
      setResult(ocrResult);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An unexpected error occurred');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  const retryBackendConnection = () => {
    setBackendStatus('checking');
    checkBackendStatus();
  };

  return (
    <main className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Certificate OCR
          </h1>
          <p className="text-lg text-gray-600 mb-6">
            Extract text from certificates and documents using advanced OCR technology
          </p>
          
          {/* Backend Status Indicator */}
          <div className="flex items-center justify-center space-x-2 mb-6">
            <div className={`w-3 h-3 rounded-full ${
              backendStatus === 'online' ? 'bg-green-500' : 
              backendStatus === 'offline' ? 'bg-red-500' : 
              'bg-yellow-500'
            }`}></div>
            <span className="text-sm text-gray-600">
              Backend: {
                backendStatus === 'online' ? 'Connected' :
                backendStatus === 'offline' ? 'Disconnected' :
                'Checking...'
              }
            </span>
            {backendStatus === 'offline' && (
              <button
                onClick={retryBackendConnection}
                className="text-sm text-primary-600 hover:text-primary-700 underline ml-2"
              >
                Retry
              </button>
            )}
          </div>
        </div>

        {/* Backend Offline Warning */}
        {backendStatus === 'offline' && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Backend Server Unavailable
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>
                    The OCR processing server is not responding. Please ensure the Flask backend is running on{' '}
                    <code className="bg-red-100 px-1 rounded">http://localhost:5000</code>
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        {result ? (
          <ResultDisplay result={result} onReset={handleReset} />
        ) : (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <FileUpload
              onFileSelect={handleFileSelect}
              isProcessing={isProcessing}
              acceptedTypes=".pdf,.png,.jpg,.jpeg,.bmp,.tiff"
            />
            
            {isProcessing && (
              <div className="mt-6 text-center">
                <div className="inline-flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                  <span className="text-primary-600 font-medium">
                    Processing your document... This may take a few moments.
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Features Section */}
        {!result && !isProcessing && (
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Multiple Formats</h3>
              <p className="text-gray-600">Support for PDF documents and various image formats including PNG, JPG, and TIFF.</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Fast Processing</h3>
              <p className="text-gray-600">Advanced OCR technology powered by Tesseract for quick and accurate text extraction.</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Secure Processing</h3>
              <p className="text-gray-600">Files are processed securely and automatically deleted after text extraction.</p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}