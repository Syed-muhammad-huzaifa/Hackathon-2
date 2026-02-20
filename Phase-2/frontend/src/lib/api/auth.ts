
/**
 * Authentication API service using Better Auth
 *
 * @spec specs/003-todo-frontend/spec.md (FR-002, FR-003, FR-004, FR-008)
 */

import { authClient } from '@/lib/auth/client';

/**
 * Sign up a new user
 */
export async function signUp(data: { name: string; email: string; password: string }) {
  const response = await authClient.signUp.email({
    name: data.name,
    email: data.email,
    password: data.password,
  });

  if (response.error) {
    throw new Error(response.error.message || 'Sign up failed');
  }

  return response.data;
}

/**
 * Sign in an existing user
 */
export async function signIn(data: { email: string; password: string }) {
  const response = await authClient.signIn.email({
    email: data.email,
    password: data.password,
    rememberMe: true,
  });

  if (response.error) {
    throw new Error(response.error.message || 'Sign in failed');
  }

  return response.data;
}

/**
 * Get current user session
 */
export async function getMe() {
  const response = await authClient.getSession();

  if (response.error || !response.data) {
    throw new Error('Not authenticated');
  }

  return response.data.user;
}

/**
 * Sign out current user
 */
export async function signOut(): Promise<void> {
  await authClient.signOut();
}

