/**
 * Main App component.
 */
import { useState } from 'react';
import './App.css';
import LoginScreen from './components/LoginScreen';
import RecordingScreen from './components/RecordingScreen';
import type { Progress } from './types';

function App() {
  const [username, setUsername] = useState<string | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);

  const handleLogin = (user: string, prog: Progress) => {
    setUsername(user);
    setProgress(prog);
  };

  const handleLogout = () => {
    setUsername(null);
    setProgress(null);
  };

  return (
    <div className="app">
      {!username || !progress ? (
        <LoginScreen onLogin={handleLogin} />
      ) : (
        <RecordingScreen
          username={username}
          initialProgress={progress}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}

export default App;

