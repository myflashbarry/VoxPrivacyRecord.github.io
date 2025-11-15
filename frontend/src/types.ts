/**
 * TypeScript type definitions for the application.
 */

export interface Progress {
  zh_pairs_done: number;
  en_pairs_done: number;
  zh_extra_questions_done: number;
  en_extra_questions_done: number;
}

export interface Task {
  language: 'zh' | 'en';
  task_type: 'pair' | 'extra_question';
  role: 'secret' | 'question';
  item_id: string;
  text: string;
}

export interface LoginResponse {
  username: string;
  progress: Progress;
}

export interface NextTaskResponse {
  username: string;
  task: Task | null;
  progress: Progress;
  message?: string;
}

export interface UploadResponse {
  status: string;
  file_path: string;
  filename: string;
  progress: Progress;
  message: string;
}

export interface RecordingState {
  isRecording: boolean;
  audioBlob: Blob | null;
  audioUrl: string | null;
}

