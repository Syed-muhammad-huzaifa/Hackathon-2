/**
 * Better Auth client configuration with JWT plugin
 *
 * @spec specs/003-todo-frontend/spec.md (FR-003, FR-007)
 */

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  plugins: [
    jwtClient(), // Enable JWT token retrieval
  ],
});

export type Session = typeof authClient.$Infer.Session;
