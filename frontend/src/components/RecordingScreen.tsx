/**
 * Main recording screen component.
 */
import { useState, useEffect } from 'react';
import { getNextTask, uploadRecording, ApiError } from '../services/api';
import type { Progress, Task } from '../types';
import ProgressBar from './ProgressBar';
import RecordingControls from './RecordingControls';

interface RecordingScreenProps {
  username: string;
  initialProgress: Progress;
  onLogout: () => void;
}

export default function RecordingScreen({ username, initialProgress, onLogout }: RecordingScreenProps) {
  const [progress, setProgress] = useState<Progress>(initialProgress);
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [allTasksComplete, setAllTasksComplete] = useState(false);

  // Fetch next task on mount and after successful upload
  useEffect(() => {
    fetchNextTask();
  }, []);

  const fetchNextTask = async () => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await getNextTask(username);
      setProgress(response.progress);

      if (response.task === null) {
        // All tasks complete
        setAllTasksComplete(true);
        setCurrentTask(null);
      } else {
        setCurrentTask(response.task);
        setAllTasksComplete(false);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to fetch next task');
    } finally {
      setLoading(false);
    }
  };

  const handleRecordingComplete = async (audioBlob: Blob) => {
    if (!currentTask) return;

    setUploading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await uploadRecording(
        username,
        currentTask.language,
        currentTask.task_type,
        currentTask.role,
        currentTask.item_id,
        audioBlob
      );

      setProgress(response.progress);
      setSuccessMessage('Recording uploaded successfully! Loading next task...');
      setUploading(false);

      // Fetch next task after short delay
      setTimeout(() => {
        fetchNextTask();
      }, 1500);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to upload recording');
      setUploading(false);
    }
  };

  const getTaskDescription = (task: Task) => {
    const langName = task.language === 'zh' ? 'Chinese' : 'English';
    
    if (task.task_type === 'instruction') {
      const warmupType = task.role === 'nobody' ? 'Nobody' : 'OnlyMe';
      return `${langName} Warm-up - ${warmupType}`;
    }
    
    const roleDesc = task.role === 'secret' ? 'Secret Text' : 'Question';
    const typeDesc = task.task_type === 'pair' ? 'Pair' : 'Extra Question';
    return `${langName} ${typeDesc} - ${roleDesc}`;
  };

  if (allTasksComplete) {
    return (
      <div className="container">
        <h1>🎉 All Tasks Complete!</h1>
        <div className="success" style={{ marginTop: '20px', fontSize: '1.1em' }}>
          Thank you for your participation, <strong>{username}</strong>!
          <br /><br />
          You have successfully completed all recording tasks:
          <ul style={{ marginTop: '10px', marginLeft: '20px' }}>
            <li>5 Chinese warm-up (Nobody)</li>
            <li>5 Chinese warm-up (OnlyMe)</li>
            <li>20 Chinese pairs (secret + question)</li>
            <li>10 extra Chinese questions</li>
            <li>5 English warm-up (Nobody)</li>
            <li>5 English warm-up (OnlyMe)</li>
            <li>20 English pairs (secret + question)</li>
            <li>10 extra English questions</li>
          </ul>
        </div>

        <ProgressBar progress={progress} />

        <button onClick={onLogout} style={{ width: '100%' }}>
          Logout
        </button>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1>Recording Task</h1>
          <p className="subtitle">Welcome, <strong>{username}</strong></p>
        </div>
        <button onClick={onLogout} style={{ background: '#6c757d' }}>
          Logout
        </button>
      </div>

      <ProgressBar progress={progress} />

      {loading && (
        <div className="loading">Loading next task</div>
      )}

      {error && (
        <div className="error">
          {error}
          <button
            onClick={fetchNextTask}
            style={{ marginTop: '10px', width: '100%' }}
          >
            Retry
          </button>
        </div>
      )}

      {successMessage && (
        <div className="success">{successMessage}</div>
      )}

      {!loading && currentTask && (
        <div>
          <div style={{
            padding: '20px',
            backgroundColor: '#fff3cd',
            border: '2px solid #ffc107',
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            <div style={{
              fontSize: '1.1em',
              fontWeight: 'bold',
              marginBottom: '10px',
              color: '#856404'
            }}>
              {getTaskDescription(currentTask)}
            </div>
            <div style={{
              fontSize: '0.9em',
              color: '#856404',
              marginBottom: '15px'
            }}>
              Item ID: {currentTask.item_id}
            </div>
            <div style={{
              fontSize: '1.3em',
              lineHeight: '1.6',
              padding: '15px',
              backgroundColor: 'white',
              borderRadius: '6px',
              minHeight: '80px',
              display: 'flex',
              alignItems: 'center'
            }}>
              {currentTask.text}
            </div>
          </div>

          <div style={{
            padding: '20px',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px'
          }}>
            <h3 style={{ marginBottom: '15px' }}>📝 Instructions:</h3>
            <ol style={{ marginLeft: '20px', lineHeight: '1.8' }}>
              <li>Read the text above carefully</li>
              <li>Click "Start Recording" and speak clearly</li>
              <li>Click "Stop Recording" when finished</li>
              <li>Click "Play" to review (optional)</li>
              <li>Click "Submit" to upload and continue</li>
            </ol>
          </div>

          <RecordingControls
            onRecordingComplete={handleRecordingComplete}
            disabled={uploading}
          />

          {uploading && (
            <div className="info" style={{ marginTop: '20px' }}>
              Uploading recording... Please wait.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

