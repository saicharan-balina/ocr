"use client";

import React, { useState } from 'react';
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
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Admin - Import Certificates</h1>
          <p className="text-gray-600">Paste JSON or CSV of certificate records and import.</p>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <label className="text-sm text-gray-700">API Key</label>
          <input className="w-full border rounded px-3 py-2 mt-1" value={apiKey} onChange={e=>setApiKey(e.target.value)} placeholder="X-API-Key" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="font-semibold">JSON</h2>
              <button onClick={importJson} disabled={isLoading} className="px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50">Import JSON</button>
            </div>
            <textarea value={jsonText} onChange={e=>setJsonText(e.target.value)} className="w-full h-72 border rounded p-2 font-mono text-sm" />
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="font-semibold">CSV</h2>
              <button onClick={importCsv} disabled={isLoading} className="px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50">Import CSV</button>
            </div>
            <textarea value={csvText} onChange={e=>setCsvText(e.target.value)} className="w-full h-72 border rounded p-2 font-mono text-sm" />
            <p className="text-xs text-gray-500 mt-2">Headers required: certificate_id,name,roll_number,course,issue_date,issuer</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Register Single Certificate (Hashed)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input type="file" onChange={e=>setRegFile(e.target.files?.[0] || null)} className="border rounded px-3 py-2" />
            <input className="border rounded px-3 py-2" placeholder="Certificate ID" value={regMeta.certificate_id} onChange={e=>setRegMeta({...regMeta, certificate_id: e.target.value})} />
            <input className="border rounded px-3 py-2" placeholder="Name" value={regMeta.name} onChange={e=>setRegMeta({...regMeta, name: e.target.value})} />
            <input className="border rounded px-3 py-2" placeholder="Roll Number" value={regMeta.roll_number} onChange={e=>setRegMeta({...regMeta, roll_number: e.target.value})} />
            <input className="border rounded px-3 py-2" placeholder="Course" value={regMeta.course} onChange={e=>setRegMeta({...regMeta, course: e.target.value})} />
            <input className="border rounded px-3 py-2" placeholder="Issue Date" value={regMeta.issue_date} onChange={e=>setRegMeta({...regMeta, issue_date: e.target.value})} />
            <input className="border rounded px-3 py-2" placeholder="Issuer" value={regMeta.issuer} onChange={e=>setRegMeta({...regMeta, issuer: e.target.value})} />
            <input className="border rounded px-3 py-2" placeholder="Issuer ID (optional)" value={regMeta.issuer_id} onChange={e=>setRegMeta({...regMeta, issuer_id: e.target.value})} />
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input type="checkbox" checked={regMeta.auto_ocr === '1'} onChange={e=>setRegMeta({...regMeta, auto_ocr: e.target.checked ? '1' : '0'})} />
              Auto-fill via OCR if fields are missing
            </label>
          </div>
          <button
            onClick={async ()=>{
              try{
                if(!regFile){ setError('Select a file'); return; }
                setIsLoading(true); setError(null); setResult(null);
                const resp = await adminApi.registerFile(regFile, regMeta as any, apiKey);
                setResult(resp);
              }catch(e:any){ setError(e?.message || 'Registration failed'); }
              finally{ setIsLoading(false); }
            }}
            className="mt-3 px-3 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50"
            disabled={isLoading}
          >Register</button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4"><p className="text-red-700">{error}</p></div>
        )}
        {result && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-2">Import Result</h3>
            <pre className="bg-gray-50 rounded p-3 text-sm">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </main>
  );
}
