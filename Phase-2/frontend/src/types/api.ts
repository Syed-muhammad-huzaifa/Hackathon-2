/**
 * API response types
 *
 * @spec specs/003-todo-frontend/spec.md (FR-037)
 */

export interface APIResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
  code?: string;
  details?: unknown;
}

export interface PaginatedResponse<T> {
  status: 'success';
  data: T[];
  meta: {
    total: number;
    page?: number;
    limit?: number;
  };
}
