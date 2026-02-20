




/**
 * Authentication API service using Backend API
 *
 * @spec specs/003-todo-frontend/spec.md (FR-002, FR-003, FR-004, FR-008)
 */

import { z } from 'zod';
import { post } from '@/lib/api/client';

// Response schemas
const AuthResponseSchema = z.object({
  status: z.string(),
  token: z.string(),
  user: z.object({
    id: z.string(),
    email: z.string(),
    name: z.string().nullable(),
  }),
});

const MeResponseSchema = z.object({
  status: z.string(),
  data: z.object({
    id: z.string(),
    email: z.string(),
    name: z.string().nullable(),
  }),
});

type AuthResponse = z.infer<typeof AuthResponseSchema>;
type MeResponse = z.infer<typeof MeResponseSchema>;

// Store JWT token in memory and localStorage
let jwtToken: string | null = null;

export function setAuthToken(token: string) {
  jwtToken = token;
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
  }
}

export function getAuthToken(): string | null {
  if (jwtToken) return jwtToken;
  if (typeof window !== 'undefined') {
    jwtToken = localStorage.getItem('auth_token');
  }
  return jwtToken;
}

export function clearAuthToken() {
  jwtToken = null;
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
  }
}

/**
 * Sign up a new user via backend API
 */
export async function signUp(data: { name: string; email: string; password: string }) {
  const response = await post<AuthResponse>(
    '/auth/sign-up',
    AuthResponseSchema,
    data,
    { skipAuth: true }
  );

  // Store JWT token
  setAuthToken(response.token);

  return response;
}

/**
 * Sign in an existing user via backend API
 */
export async function signIn(data: { email: string; password: string }) {
  const response = await post<AuthResponse>(
    '/auth/sign-in',
    AuthResponseSchema,
    { ...data, rememberMe: true },
    { skipAuth: true }
  );

  // Store JWT token
  setAuthToken(response.token);

  return response;
}

/**
 * Get current user session from backend
 */
export async function getMe() {
  const { get } = await import('@/lib/api/client');
  const response = await get<MeResponse>(
    '/auth/me',
    MeResponseSchema
  );

  return response.data;
}

/**
 * Sign out current user
 */
export async function signOut(): Promise<void> {
  clearAuthToken();
  // Redirect to sign-in page
  if (typeof window !== 'undefined') {
    window.location.href = '/sign-in';
  }
}

