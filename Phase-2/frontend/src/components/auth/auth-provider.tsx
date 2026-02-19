/**
 * Authentication Provider Component
 *
 * Wraps the app to provide reactive auth state to all components.
 *
 * @spec specs/003-todo-frontend/spec.md (FR-003)
 */

'use client';

import { ReactNode } from 'react';

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Auth Provider - wraps app to enable reactive session state
 *
 * Better Auth client automatically manages session state via nano-store,
 * so we just need to ensure the client is initialized.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  return <>{children}</>;
}
