/**
 * Progress bar component to display recording progress.
 */
import type { Progress } from '../types';

interface ProgressBarProps {
  progress: Progress;
}

const ProgressItem = ({ label, current, total }: { label: string; current: number; total: number }) => {
  const percentage = (current / total) * 100;
  const isComplete = current >= total;

  return (
    <div style={{ marginBottom: '15px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
        <span style={{ fontWeight: '500' }}>{label}</span>
        <span style={{ color: isComplete ? '#28a745' : '#666' }}>
          {current} / {total} {isComplete && '✓'}
        </span>
      </div>
      <div style={{
        height: '8px',
        backgroundColor: '#e9ecef',
        borderRadius: '4px',
        overflow: 'hidden'
      }}>
        <div style={{
          height: '100%',
          width: `${percentage}%`,
          backgroundColor: isComplete ? '#28a745' : '#667eea',
          transition: 'width 0.3s ease'
        }} />
      </div>
    </div>
  );
};

export default function ProgressBar({ progress }: ProgressBarProps) {
  const totalCompleted = 
    progress.zh_pairs_done + 
    progress.en_pairs_done + 
    progress.zh_extra_questions_done + 
    progress.en_extra_questions_done;
  const totalRequired = 20 + 20 + 10 + 10; // 60 total tasks

  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#f8f9fa',
      borderRadius: '8px',
      marginBottom: '30px'
    }}>
      <h2 style={{ marginBottom: '20px', fontSize: '1.3em' }}>Your Progress</h2>
      
      <ProgressItem 
        label="Chinese Pairs (secret + question)" 
        current={progress.zh_pairs_done} 
        total={20} 
      />
      
      <ProgressItem 
        label="Extra Chinese Questions" 
        current={progress.zh_extra_questions_done} 
        total={10} 
      />
      
      <ProgressItem 
        label="English Pairs (secret + question)" 
        current={progress.en_pairs_done} 
        total={20} 
      />
      
      <ProgressItem 
        label="Extra English Questions" 
        current={progress.en_extra_questions_done} 
        total={10} 
      />

      <div style={{
        marginTop: '20px',
        paddingTop: '15px',
        borderTop: '2px solid #dee2e6',
        display: 'flex',
        justifyContent: 'space-between',
        fontWeight: 'bold',
        fontSize: '1.1em'
      }}>
        <span>Total Progress:</span>
        <span style={{ color: totalCompleted === totalRequired ? '#28a745' : '#667eea' }}>
          {totalCompleted} / {totalRequired}
        </span>
      </div>
    </div>
  );
}

