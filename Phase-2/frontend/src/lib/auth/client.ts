/**
 * Better Auth client configuration with JWT plugin
 *
 * @spec specs/003-todo-frontend/spec.md (FR-003, FR-007)
 */

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [
    jwtClient(), // Enable JWT token retrieval
  ],
});

export type Session = typeof authClient.$Infer.Session;
