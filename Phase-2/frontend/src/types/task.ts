/**
 * Task types
 *
 * @spec specs/003-todo-frontend/spec.md (FR-015, FR-016, FR-017, FR-020, FR-024)
 */

export type TaskStatus = 'pending' | 'in-progress' | 'completed' | 'deleted';
export type TaskPriority = 'low' | 'medium' | 'high';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  created_at: string;
  updated_at: string;
}

export interface TaskListState {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
}

export interface TaskAnalytics {
  statusDistribution: {
    pending: number;
    'in-progress': number;
    completed: number;
  };
  priorityDistribution: {
    low: number;
    medium: number;
    high: number;
  };
  completionTrend: {
    date: string;
    completed: number;
  }[];
}
