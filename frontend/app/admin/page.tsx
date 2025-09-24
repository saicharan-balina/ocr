"use client";

import React, { useEffect, useState } from 'react';
import { adminApi, ImportResponse } from '@/lib/api';

export default function AdminPage() {
  const [jsonText, setJsonText] = useState('[\n  {"certificate_id":"JH-UNI-2022-0001","name":"Amit Kumar","roll_number":"19CS1234","course":"B.Tech CSE","issue_date":"2022-07-15","issuer":"XYZ University"}\n]');
  const [csvText, setCsvText] = useState('certificate_id,name,roll_number,course,issue_date,issuer\nJH-UNI-2022-0001,Amit Kumar,19CS1234,B.Tech CSE,2022-07-15,XYZ University');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ImportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState('demo-admin-key');
  const [regFile, setRegFile] = useState<File | null>(null);
  const [regMeta, setRegMeta] = useState({ certificate_id: '', name: '', roll_number: '', course: '', issue_date: '', issuer: '', issuer_id: '', auto_ocr: '1' });
  const [stats, setStats] = useState<any | null>(null);
  const [certificates, setCertificates] = useState<any[]>([]);
  const [showImportSection, setShowImportSection] = useState(false);

  useEffect(() => {
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadDashboardData = async () => {
    try {
      const s = await adminApi.stats(apiKey);
      setStats(s?.stats || s);
      
      // Load certificates list
      const resp = await fetch(`http://localhost:5000/api/admin/records?limit=10`, {
        headers: { 'X-API-Key': apiKey }
      });
      if (resp.ok) {
        const data = await resp.json();
        setCertificates(data.items || []);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

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

  return (
    <main className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
              </svg>
            </div>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-4">
            CryptoCert Dashboard
          </h1>
          <p className="text-lg text-gray-300">
            Professional Certificate Verification & Management System
          </p>
        </div>

        {/* API Key Configuration */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
          <label className="text-sm text-gray-300 block mb-2">API Authentication Key</label>
          <input 
            className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent" 
            value={apiKey} 
            onChange={e=>setApiKey(e.target.value)} 
            placeholder="Enter your API key" 
          />
        </div>

        {/* Dashboard Stats */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-sm rounded-xl border border-white/10 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Total Certificates</p>
                  <p className="text-3xl font-bold text-white">{stats.certificates}</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/30 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 2L3 7v11a1 1 0 001 1h12a1 1 0 001-1V7l-7-5zM9 9a1 1 0 112 0v4a1 1 0 11-2 0V9z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-sm rounded-xl border border-white/10 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Active Issuers</p>
                  <p className="text-3xl font-bold text-white">{stats.issuers}</p>
                </div>
                <div className="w-12 h-12 bg-green-500/30 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-sm rounded-xl border border-white/10 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Verification Logs</p>
                  <p className="text-3xl font-bold text-white">{stats.logs}</p>
                </div>
                <div className="w-12 h-12 bg-purple-500/30 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-purple-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Certificates List */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">Recent Certificates</h2>
            <button 
              onClick={() => setShowImportSection(!showImportSection)}
              className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg hover:from-cyan-600 hover:to-blue-700 transition-all duration-200 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
              {showImportSection ? 'Hide Import' : 'Import Certificates'}
            </button>
          </div>

          {certificates.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-gray-300 font-medium">Certificate ID</th>
                    <th className="text-left py-3 px-4 text-gray-300 font-medium">Name</th>
                    <th className="text-left py-3 px-4 text-gray-300 font-medium">Course</th>
                    <th className="text-left py-3 px-4 text-gray-300 font-medium">Issuer</th>
                    <th className="text-left py-3 px-4 text-gray-300 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {certificates.map((cert, index) => (
                    <tr key={index} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="py-3 px-4 text-cyan-400 font-mono text-sm">{cert.certificate_id || 'N/A'}</td>
                      <td className="py-3 px-4 text-white">{cert.name || 'N/A'}</td>
                      <td className="py-3 px-4 text-gray-300">{cert.course || 'N/A'}</td>
                      <td className="py-3 px-4 text-gray-300">{cert.issuer || 'N/A'}</td>
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-500/20 text-green-300 border border-green-500/30">
                          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          Verified
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-gray-400 text-lg">No certificates found</p>
              <p className="text-gray-500 text-sm">Start by importing or registering your first certificate</p>
            </div>
          )}
        </div>

        {/* Import Section - Collapsible */}
        {showImportSection && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <svg className="w-5 h-5 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    JSON Import
                  </h3>
                  <button 
                    onClick={importJson} 
                    disabled={isLoading} 
                    className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 transition-all duration-200"
                  >
                    Import JSON
                  </button>
                </div>
                <textarea 
                  value={jsonText} 
                  onChange={e=>setJsonText(e.target.value)} 
                  className="w-full h-64 bg-black/30 border border-white/20 rounded-lg p-4 text-white font-mono text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent" 
                  placeholder="Paste your JSON data here..."
                />
              </div>

              <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                    CSV Import
                  </h3>
                  <button 
                    onClick={importCsv} 
                    disabled={isLoading} 
                    className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 transition-all duration-200"
                  >
                    Import CSV
                  </button>
                </div>
                <textarea 
                  value={csvText} 
                  onChange={e=>setCsvText(e.target.value)} 
                  className="w-full h-64 bg-black/30 border border-white/20 rounded-lg p-4 text-white font-mono text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
                  placeholder="certificate_id,name,roll_number,course,issue_date,issuer"
                />
                <p className="text-xs text-gray-400 mt-2">Required headers: certificate_id, name, roll_number, course, issue_date, issuer</p>
              </div>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
              <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                <svg className="w-5 h-5 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                Register Certificate with File Hash
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="col-span-full">
                  <label className="block text-sm text-gray-300 mb-2">Certificate File</label>
                  <input 
                    type="file" 
                    onChange={e=>setRegFile(e.target.files?.[0] || null)} 
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-gradient-to-r file:from-cyan-500 file:to-blue-600 file:text-white file:cursor-pointer hover:file:from-cyan-600 hover:file:to-blue-700"
                  />
                </div>
                <input 
                  className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
                  placeholder="Certificate ID" 
                  value={regMeta.certificate_id} 
                  onChange={e=>setRegMeta({...regMeta, certificate_id: e.target.value})} 
                />
                <input 
                  className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
                  placeholder="Student Name" 
                  value={regMeta.name} 
                  onChange={e=>setRegMeta({...regMeta, name: e.target.value})} 
                />
                <input 
                  className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
                  placeholder="Roll Number" 
                  value={regMeta.roll_number} 
                  onChange={e=>setRegMeta({...regMeta, roll_number: e.target.value})} 
                />
                <input 
                  className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
                  placeholder="Course" 
                  value={regMeta.course} 
                  onChange={e=>setRegMeta({...regMeta, course: e.target.value})} 
                />
                <input 
                  className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
                  placeholder="Issue Date" 
                  value={regMeta.issue_date} 
                  onChange={e=>setRegMeta({...regMeta, issue_date: e.target.value})} 
                />
                <input 
                  className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
                  placeholder="Issuer" 
                  value={regMeta.issuer} 
                  onChange={e=>setRegMeta({...regMeta, issuer: e.target.value})} 
                />
                <input 
                  className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
                  placeholder="Issuer ID (optional)" 
                  value={regMeta.issuer_id} 
                  onChange={e=>setRegMeta({...regMeta, issuer_id: e.target.value})} 
                />
              </div>
              <div className="flex items-center justify-between mt-6">
                <label className="flex items-center gap-2 text-sm text-gray-300">
                  <input 
                    type="checkbox" 
                    checked={regMeta.auto_ocr === '1'} 
                    onChange={e=>setRegMeta({...regMeta, auto_ocr: e.target.checked ? '1' : '0'})} 
                    className="w-4 h-4 text-purple-600 bg-white/10 border-white/20 rounded focus:ring-purple-500 focus:ring-2"
                  />
                  Auto-fill via OCR if fields are missing
                </label>
                <button
                  onClick={async ()=>{
                    try{
                      if(!regFile){ setError('Please select a file'); return; }
                      setIsLoading(true); setError(null); setResult(null);
                      const resp = await adminApi.registerFile(regFile, regMeta as any, apiKey);
                      setResult(resp);
                      loadDashboardData(); // Refresh data
                    }catch(e:any){ setError(e?.message || 'Registration failed'); }
                    finally{ setIsLoading(false); }
                  }}
                  className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-700 disabled:opacity-50 transition-all duration-200 flex items-center gap-2"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Processing...
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
          </div>
        )}

        {/* Results and Errors */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <h3 className="text-red-300 font-medium">Operation Failed</h3>
                <p className="text-red-200 text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}
        
        {result && (
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-6 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-4">
              <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <h3 className="text-green-300 font-semibold">Operation Successful</h3>
            </div>
            <div className="bg-black/30 rounded-lg p-4">
              <pre className="text-green-100 text-sm overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
