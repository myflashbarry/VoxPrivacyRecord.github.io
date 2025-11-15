/**
 * Login screen component for user identification.
 */
import { useState } from 'react';
import { login, testConnection } from '../services/api';
import type { Progress } from '../types';

interface LoginScreenProps {
  onLogin: (username: string, progress: Progress) => void;
}

export default function LoginScreen({ onLogin }: LoginScreenProps) {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<boolean | null>(null);

  const checkConnection = async () => {
    const isConnected = await testConnection();
    setConnectionStatus(isConnected);
    return isConnected;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    setLoading(true);

    try {
      // Test connection first
      const isConnected = await checkConnection();
      if (!isConnected) {
        setError('Cannot connect to backend server. Please make sure the backend is running.');
        setLoading(false);
        return;
      }

      // Login
      const response = await login(username.trim());
      onLogin(response.username, response.progress);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>VoxPrivacyRecord</h1>
      <p className="subtitle">Speech Data Collection for ICLR 2026</p>

      {connectionStatus === false && (
        <div className="error">
          ⚠️ Backend server is not reachable. Please start the backend server first.
        </div>
      )}

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="username" style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
            Enter your username:
          </label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g., alice, bob, researcher01"
            disabled={loading}
            autoFocus
          />
        </div>

        <button type="submit" disabled={loading} style={{ width: '100%' }}>
          {loading ? 'Logging in...' : 'Start Recording Tasks'}
        </button>
      </form>

      <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
        <h3 style={{ marginBottom: '10px', fontSize: '1.1em' }}>What you'll do (in order):</h3>
        <ul style={{ marginLeft: '20px', lineHeight: '1.8' }}>
          <li>Record <strong>5 Chinese warm-up sentences (Nobody)</strong></li>
          <li>Record <strong>5 Chinese warm-up sentences (OnlyMe)</strong></li>
          <li>Record <strong>20 Chinese pairs</strong> (secret + question)</li>
          <li>Record <strong>10 additional Chinese questions</strong></li>
          <li>Record <strong>5 English warm-up sentences (Nobody)</strong></li>
          <li>Record <strong>5 English warm-up sentences (OnlyMe)</strong></li>
          <li>Record <strong>20 English pairs</strong> (secret + question)</li>
          <li>Record <strong>10 additional English questions</strong></li>
        </ul>
        <p style={{ marginTop: '15px', color: '#666', fontSize: '0.9em' }}>
          You'll start with warm-up sentences before the main recording tasks. Each pair consists of two recordings: one for the secret text, and one for the question about that secret.
        </p>
      </div>
    </div>
  );
}

