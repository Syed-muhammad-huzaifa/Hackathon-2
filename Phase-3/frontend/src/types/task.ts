// Task types for analytics display

export type TaskStatus = "pending" | "in_progress" | "completed" | "deleted";

export interface Task {
  id: string;
  userId: string;
  title: string;
  description?: string | null;
  status: TaskStatus;
  createdAt: string;
  updatedAt: string;
}

export interface TaskStatusData {
  name: string;
  value: number;
  color: string;
}

export interface TaskTrendData {
  date: string;
  completed: number;
  created: number;
}

export interface AnalyticsState {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
}
