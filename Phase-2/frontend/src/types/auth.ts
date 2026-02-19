/**
 * Authentication types
 *
 * @spec specs/003-todo-frontend/spec.md (FR-002, FR-003, FR-004)
 */

export interface User {
  id: string;
  email: string;
  name: string | null;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

export interface SignUpData {
  name: string;
  email: string;
  password: string;
}

export interface SignInData {
  email: string;
  password: string;
}
