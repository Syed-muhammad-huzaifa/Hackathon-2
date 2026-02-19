/**
 * Better Auth API route handler
 *
 * Handles all Better Auth endpoints:
 * - POST /api/auth/sign-up
 * - POST /api/auth/sign-in
 * - POST /api/auth/sign-out
 * - GET /api/auth/session
 * - GET /.well-known/jwks.json
 *
 * @spec specs/003-todo-frontend/spec.md (FR-002, FR-003, FR-004, FR-007, FR-008)
 */

import { auth } from "@/lib/auth/server";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
