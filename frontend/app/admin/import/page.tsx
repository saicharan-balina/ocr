"use client";

import React, { useState } from 'react';
import { adminApi, ImportResponse } from '@/lib/api';

export default function AdminImportPage() {
  const [apiKey, setApiKey] = useState('demo-admin-key');
  const [jsonText, setJsonText] = useState('[\n  {"certificate_id":"JH-UNI-2022-0001","name":"Amit Kumar","roll_number":"19CS1234","course":"B.Tech CSE","issue_date":"2022-07-15","issuer":"XYZ University"}\n]');
  const [csvText, setCsvText] = useState('certificate_id,name,roll_number,course,issue_date,issuer\nJH-UNI-2022-0001,Amit Kumar,19CS1234,B.Tech CSE,2022-07-15,XYZ University');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ImportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const parseCsv = (text: string): any[] => {
    const lines = text.split(/\r?\n/).filter(Boolean);
    if (lines.length < 2) return [];
    const headers = lines[0].split(',').map(h => h.trim());
    return lines.slice(1).map(line => {
      const vals = line.split(',');
      const obj: any = {};
      headers.forEach((h, i) => obj[h] = (vals[i] || '').trim());
      return obj;
    });
  };

  const importJson = async () => {
    try {
      setIsLoading(true); setError(null); setResult(null);
      const records = JSON.parse(jsonText);
      if (!Array.isArray(records)) throw new Error('JSON must be an array');
      const resp = await adminApi.importRecords(records, apiKey);
      setResult(resp);
    } catch (e: any) {
      setError(e?.message || 'Import failed');
    } finally { setIsLoading(false); }
  };

  const importCsv = async () => {
    try {
      setIsLoading(true); setError(null); setResult(null);
      const records = parseCsv(csvText);
      const resp = await adminApi.importRecords(records, apiKey);
      setResult(resp);
    } catch (e: any) {
      setError(e?.message || 'Import failed');
    } finally { setIsLoading(false); }
  };

  // Register with file
  const [regFile, setRegFile] = useState<File | null>(null);
  const [regMeta, setRegMeta] = useState({ certificate_id: '', name: '', roll_number: '', course: '', issue_date: '', issuer: '', issuer_id: '', auto_ocr: '1' });

  const handleRegister = async () => {
    try{
      if(!regFile){ setError('Please select a file'); return; }
      setIsLoading(true); setError(null); setResult(null);
      const resp = await adminApi.registerFile(regFile, regMeta as any, apiKey);
      setResult(resp);
    }catch(e:any){ setError(e?.message || 'Registration failed'); }
    finally{ setIsLoading(false); }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-4">
            Import & Register
          </h1>
          <p className="text-lg text-gray-300">
            Bulk import certificates or register individual files
          </p>
          <div className="flex justify-center mt-4">
            <a 
              className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-700 transition-all duration-200 flex items-center gap-2" 
              href="/admin"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
              Back to Dashboard
            </a>
          </div>
        </div>

        {/* API Key Configuration */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
          <label className="text-sm text-gray-300 block mb-2">API Authentication Key</label>
          <input 
            className="w-full bg-white/10 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent" 
            value={apiKey} 
            onChange={e=>setApiKey(e.target.value)} 
            placeholder="Enter your API key" 
          />
        </div>

        {/* Import Methods */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-sm rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-green-500/30 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-green-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-white">JSON Import</h3>
              </div>
              <button 
                onClick={importJson} 
                disabled={isLoading} 
                className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {isLoading ? 'Importing...' : 'Import JSON'}
              </button>
            </div>
            <textarea 
              value={jsonText} 
              onChange={e=>setJsonText(e.target.value)} 
              className="w-full h-64 bg-white/10 border border-white/30 rounded-lg p-4 text-white font-mono text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none" 
              placeholder="Paste your JSON array here..."
            />
          </div>

          <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-sm rounded-xl border border-white/10 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-500/30 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clipRule="evenodd" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-white">CSV Import</h3>
              </div>
              <button 
                onClick={importCsv} 
                disabled={isLoading} 
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-600 text-white rounded-lg hover:from-blue-600 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {isLoading ? 'Importing...' : 'Import CSV'}
              </button>
            </div>
            <textarea 
              value={csvText} 
              onChange={e=>setCsvText(e.target.value)} 
              className="w-full h-64 bg-white/10 border border-white/30 rounded-lg p-4 text-white font-mono text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none" 
              placeholder="Paste your CSV data here..."
            />
            <p className="text-xs text-gray-300 mt-2 flex items-center gap-2">
              <svg className="w-3 h-3 text-blue-300" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              Required headers: certificate_id, name, roll_number, course, issue_date, issuer
            </p>
          </div>
        </div>

        {/* File Registration */}
        <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-sm rounded-xl border border-white/10 p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-purple-500/30 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-300" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white">Register Certificate with File Hash</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="col-span-full">
              <label className="block text-sm text-gray-300 mb-2 flex items-center gap-2">
                <svg className="w-4 h-4 text-purple-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                Certificate File
              </label>
              <input 
                type="file" 
                onChange={e=>setRegFile(e.target.files?.[0] || null)} 
                className="w-full bg-white/10 border border-white/30 rounded-lg px-4 py-3 text-white file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-purple-500/50 file:text-white hover:file:bg-purple-500/60 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
              />
            </div>
            <input 
              className="bg-white/10 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
              placeholder="Certificate ID" 
              value={regMeta.certificate_id} 
              onChange={e=>setRegMeta({...regMeta, certificate_id: e.target.value})} 
            />
            <input 
              className="bg-white/10 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
              placeholder="Student Name" 
              value={regMeta.name} 
              onChange={e=>setRegMeta({...regMeta, name: e.target.value})} 
            />
            <input 
              className="bg-white/10 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
              placeholder="Roll Number" 
              value={regMeta.roll_number} 
              onChange={e=>setRegMeta({...regMeta, roll_number: e.target.value})} 
            />
            <input 
              className="bg-white/10 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
              placeholder="Course" 
              value={regMeta.course} 
              onChange={e=>setRegMeta({...regMeta, course: e.target.value})} 
            />
            <input 
              className="bg-white/10 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
              placeholder="Issue Date (YYYY-MM-DD)" 
              value={regMeta.issue_date} 
              onChange={e=>setRegMeta({...regMeta, issue_date: e.target.value})} 
            />
            <input 
              className="bg-white/10 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
              placeholder="Issuer" 
              value={regMeta.issuer} 
              onChange={e=>setRegMeta({...regMeta, issuer: e.target.value})} 
            />
            <input 
              className="bg-white/10 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
              placeholder="Issuer ID (optional)" 
              value={regMeta.issuer_id} 
              onChange={e=>setRegMeta({...regMeta, issuer_id: e.target.value})} 
            />
          </div>
          <div className="flex items-center justify-between mt-6">
            <label className="flex items-center gap-3 text-sm text-gray-300">
              <input 
                type="checkbox" 
                checked={regMeta.auto_ocr === '1'} 
                onChange={e=>setRegMeta({...regMeta, auto_ocr: e.target.checked ? '1' : '0'})} 
                className="w-4 h-4 text-purple-500 bg-white/10 border-white/30 rounded focus:ring-purple-500 focus:ring-2" 
              />
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4 text-purple-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 2L3 7v11a1 1 0 001 1h12a1 1 0 001-1V7l-7-5zM9 9a1 1 0 112 0v4a1 1 0 11-2 0V9z" clipRule="evenodd" />
                </svg>
                Auto-fill via OCR if fields are missing
              </span>
            </label>
            <button 
              onClick={handleRegister} 
              disabled={isLoading} 
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Registering...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                  </svg>
                  Register Certificate
                </>
              )}
            </button>
          </div>
        </div>

        {/* Status Messages */}
        {error && (
          <div className="bg-red-500/20 backdrop-blur-sm border border-red-500/30 rounded-xl p-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-500/30 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-red-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="text-red-200 font-semibold">Operation Failed</h3>
                <p className="text-red-300 text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}
        
        {result && (
          <div className="bg-green-500/20 backdrop-blur-sm border border-green-500/30 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-green-500/30 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-green-300" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-green-200 font-semibold text-lg">Operation Successful</h3>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <pre className="text-gray-200 text-sm overflow-x-auto font-mono">{JSON.stringify(result, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
