/**
 * Recording controls component using MediaRecorder API.
 */
import { useState, useRef, useEffect } from 'react';
import type { RecordingState } from '../types';

interface RecordingControlsProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  disabled?: boolean;
}

export default function RecordingControls({ onRecordingComplete, disabled = false }: RecordingControlsProps) {
  const [recordingState, setRecordingState] = useState<RecordingState>({
    isRecording: false,
    audioBlob: null,
    audioUrl: null,
  });
  const [error, setError] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (recordingState.audioUrl) {
        URL.revokeObjectURL(recordingState.audioUrl);
      }
    };
  }, []);

  const startRecording = async () => {
    setError(null);
    audioChunksRef.current = [];
    setRecordingTime(0);

    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      mediaRecorderRef.current = mediaRecorder;

      // Collect audio chunks
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);

        setRecordingState({
          isRecording: false,
          audioBlob,
          audioUrl,
        });

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());

        // Clear timer
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
      };

      // Start recording
      mediaRecorder.start();

      setRecordingState(prev => ({
        ...prev,
        isRecording: true,
        audioBlob: null,
        audioUrl: null,
      }));

      // Start timer
      timerRef.current = window.setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to access microphone. Please grant permission and try again.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recordingState.isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  const playRecording = () => {
    if (recordingState.audioUrl) {
      const audio = new Audio(recordingState.audioUrl);
      audio.play();
    }
  };

  const submitRecording = () => {
    if (recordingState.audioBlob) {
      onRecordingComplete(recordingState.audioBlob);
      // Reset state
      setRecordingState({
        isRecording: false,
        audioBlob: null,
        audioUrl: null,
      });
      setRecordingTime(0);
    }
  };

  const discardRecording = () => {
    if (recordingState.audioUrl) {
      URL.revokeObjectURL(recordingState.audioUrl);
    }
    setRecordingState({
      isRecording: false,
      audioBlob: null,
      audioUrl: null,
    });
    setRecordingTime(0);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div style={{ marginTop: '20px' }}>
      {error && (
        <div className="error" style={{ marginBottom: '15px' }}>
          {error}
        </div>
      )}

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        alignItems: 'center'
      }}>
        {recordingState.isRecording && (
          <div style={{
            fontSize: '2em',
            fontWeight: 'bold',
            color: '#dc3545',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <span style={{
              width: '12px',
              height: '12px',
              backgroundColor: '#dc3545',
              borderRadius: '50%',
              animation: 'pulse 1.5s ease-in-out infinite'
            }} />
            Recording: {formatTime(recordingTime)}
          </div>
        )}

        {!recordingState.isRecording && recordingState.audioBlob && (
          <div style={{
            fontSize: '1.2em',
            color: '#28a745',
            fontWeight: '500'
          }}>
            ✓ Recording complete ({formatTime(recordingTime)})
          </div>
        )}

        <div style={{
          display: 'flex',
          gap: '10px',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          {!recordingState.isRecording && !recordingState.audioBlob && (
            <button
              onClick={startRecording}
              disabled={disabled}
              style={{ minWidth: '150px' }}
            >
              🎤 Start Recording
            </button>
          )}

          {recordingState.isRecording && (
            <button
              onClick={stopRecording}
              style={{ minWidth: '150px', background: '#dc3545' }}
            >
              ⏹ Stop Recording
            </button>
          )}

          {!recordingState.isRecording && recordingState.audioBlob && (
            <>
              <button
                onClick={playRecording}
                style={{ minWidth: '120px', background: '#17a2b8' }}
              >
                ▶️ Play
              </button>
              <button
                onClick={submitRecording}
                disabled={disabled}
                style={{ minWidth: '120px', background: '#28a745' }}
              >
                ✓ Submit
              </button>
              <button
                onClick={discardRecording}
                style={{ minWidth: '120px', background: '#6c757d' }}
              >
                🗑 Discard
              </button>
            </>
          )}
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  );
}

