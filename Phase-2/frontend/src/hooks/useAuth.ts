/**
 * React hook for authentication state management
 *
 * Provides reactive user state that updates automatically on login/logout.
 *
 * @spec specs/003-todo-frontend/spec.md (FR-003, FR-007)
 */

'use client';

import { authClient } from '@/lib/auth/client';

/**
 * Hook to access current user session with reactive updates
 *
 * @returns {Object} Session data with user, loading state, and error
 *
 * @example
 * ```tsx
 * function UserProfile() {
 *   const { data: session, isPending, error } = useAuth();
 *
 *   if (isPending) return <div>Loading...</div>;
 *   if (error) return <div>Error: {error.message}</div>;
 *   if (!session) return <div>Not logged in</div>;
 *
 *   return <div>Welcome, {session.user.name}</div>;
 * }
 * ```
 */
export function useAuth() {
  return authClient.useSession();
}

/**
 * Hook to get current user (shorthand)
 *
 * @returns User object or null if not authenticated
 */
export function useUser() {
  const { data: session } = useAuth();
  return session?.user ?? null;
}
