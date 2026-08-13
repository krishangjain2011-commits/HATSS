import { useState } from 'react';

export default function ESP32Debug() {
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const testConnection = async () => {
    setLoading(true);
    setStatus('idle');
    setResult('Testing connection to 192.168.4.1...\n');

    try {
      const response = await fetch('http://192.168.4.1/api/sensors', {
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      setResult(prev => prev + `✓ Response received (Status: ${response.status})\n`);

      if (response.ok) {
        const data = await response.json();
        setResult(prev => prev + `✓ JSON parsed successfully\n\n`);
        setResult(prev => prev + `Data:\n${JSON.stringify(data, null, 2)}`);
        setStatus('success');
      } else {
        setResult(prev => prev + `✗ Response not OK: ${response.statusText}\n`);
        setStatus('error');
      }
    } catch (error) {
      setResult(prev => prev + `✗ Error: ${error instanceof Error ? error.message : String(error)}\n`);
      setStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const testBackend = async () => {
    setLoading(true);
    setStatus('idle');
    setResult('Testing connection to backend...\n');

    try {
      const response = await fetch('/api/v1/sensors/status');
      setResult(prev => prev + `✓ Response received (Status: ${response.status})\n`);

      if (response.ok) {
        const data = await response.json();
        setResult(prev => prev + `✓ JSON parsed successfully\n\n`);
        setResult(prev => prev + `Data:\n${JSON.stringify(data, null, 2)}`);
        setStatus('success');
      } else {
        setResult(prev => prev + `✗ Response not OK: ${response.statusText}\n`);
        setStatus('error');
      }
    } catch (error) {
      setResult(prev => prev + `✗ Error: ${error instanceof Error ? error.message : String(error)}\n`);
      setStatus('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-950 text-white p-8 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">ESP32 Debug Console</h1>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <button
          onClick={testConnection}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-4 py-2 rounded font-semibold"
        >
          {loading ? 'Testing...' : 'Test ESP32 (192.168.4.1)'}
        </button>
        <button
          onClick={testBackend}
          disabled={loading}
          className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 px-4 py-2 rounded font-semibold"
        >
          {loading ? 'Testing...' : 'Test Backend'}
        </button>
      </div>

      <div className={`mb-4 p-3 rounded text-sm font-semibold ${
        status === 'success' ? 'bg-green-500/20 text-green-400 border border-green-500' :
        status === 'error' ? 'bg-red-500/20 text-red-400 border border-red-500' :
        'bg-slate-800 text-slate-400'
      }`}>
        {status === 'idle' ? 'Ready to test' :
         status === 'success' ? '✓ Connection Successful' :
         '✗ Connection Failed'}
      </div>

      <div className="bg-slate-900 border border-slate-700 rounded p-4 font-mono text-sm">
        <pre className="whitespace-pre-wrap overflow-auto max-h-96">
          {result || 'Click a button to test connection...'}
        </pre>
      </div>

      <div className="mt-6 bg-slate-800 rounded p-4 text-sm">
        <h2 className="font-bold mb-2">Checklist:</h2>
        <ul className="space-y-1 text-slate-300">
          <li>✓ Connected to HATSS_SECURITY_NET WiFi?</li>
          <li>✓ ESP32 powered on and running?</li>
          <li>✓ Serial Monitor showing no errors?</li>
          <li>✓ Opening from same network as ESP32?</li>
          <li>✓ Browser allows insecure origin access?</li>
        </ul>
      </div>
    </div>
  );
}
