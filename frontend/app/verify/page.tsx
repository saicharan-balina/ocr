"use client";

import React, { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import { verifyApi, VerifyResponse } from '@/lib/api';

export default function VerifyPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [verdict, setVerdict] = useState<VerifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fields, setFields] = useState({ certificate_id: '', name: '', roll_number: '', course: '' });

  const onFileSelect = async (file: File) => {
    setIsProcessing(true);
    setError(null);
    setVerdict(null);
    try {
      const resp = await verifyApi.byFile(file);
      setVerdict(resp);
    } catch (e: any) {
      setError(e?.message || 'Verification failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const submitFields = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setError(null);
    setVerdict(null);
    try {
      const payload: any = {};
      if (fields.certificate_id) payload.certificate_id = fields.certificate_id;
      if (fields.name) payload.name = fields.name;
      if (fields.roll_number) payload.roll_number = fields.roll_number;
      if (fields.course) payload.course = fields.course;
      const resp = await verifyApi.byFields(payload);
      setVerdict(resp);
    } catch (e: any) {
      setError(e?.message || 'Verification failed');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <main className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Verify Certificate</h1>
          <p className="text-gray-600">Upload a file or enter fields to check authenticity.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="font-semibold mb-4">Verify by File</h2>
            <FileUpload onFileSelect={onFileSelect} isProcessing={isProcessing} acceptedTypes=".pdf,.png,.jpg,.jpeg,.bmp,.tiff" />
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="font-semibold mb-4">Verify by Fields</h2>
            <form onSubmit={submitFields} className="space-y-3">
              <input className="w-full border rounded px-3 py-2" placeholder="Certificate ID" value={fields.certificate_id} onChange={e=>setFields({...fields, certificate_id: e.target.value})} />
              <input className="w-full border rounded px-3 py-2" placeholder="Name" value={fields.name} onChange={e=>setFields({...fields, name: e.target.value})} />
              <input className="w-full border rounded px-3 py-2" placeholder="Roll Number" value={fields.roll_number} onChange={e=>setFields({...fields, roll_number: e.target.value})} />
              <input className="w-full border rounded px-3 py-2" placeholder="Course" value={fields.course} onChange={e=>setFields({...fields, course: e.target.value})} />
              <button type="submit" className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50" disabled={isProcessing}>Verify</button>
            </form>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {verdict && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Result</h3>
              <span className={`px-3 py-1 rounded text-white ${verdict.verdict === 'valid' ? 'bg-green-600' : 'bg-red-600'}`}>
                {verdict.verdict?.toUpperCase()}
              </span>
            </div>
            <div className="mt-4 text-sm text-gray-700">
              <p>Matched By: {verdict.matched_by || 'N/A'}</p>
            </div>
            {verdict.record && (
              <pre className="mt-4 p-3 bg-gray-50 rounded text-xs overflow-auto">{JSON.stringify(verdict.record, null, 2)}</pre>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
