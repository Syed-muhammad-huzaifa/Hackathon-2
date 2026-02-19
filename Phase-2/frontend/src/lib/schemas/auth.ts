/**
 * Authentication API contracts
 *
 * @spec specs/003-todo-frontend/spec.md (FR-002, FR-003, FR-004)
 */

import { z } from 'zod'

// ============================================================================
// Types
// ============================================================================

export type User = z.infer<typeof UserSchema>
export type SignUpRequest = z.infer<typeof SignUpRequestSchema>
export type SignInRequest = z.infer<typeof SignInRequestSchema>
export type AuthResponse = z.infer<typeof AuthResponseSchema>
export type MeResponse = z.infer<typeof MeResponseSchema>

// ============================================================================
// Zod Schemas
// ============================================================================

export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().nullable(),
})

export const SignUpRequestSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  email: z.string().email('Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export const SignInRequestSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(1, 'Password is required'),
})

export const AuthResponseSchema = z.object({
  status: z.literal('success'),
  token: z.string(),
  user: UserSchema,
})

export const MeResponseSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().nullable(),
})

// ============================================================================
// Error Response Schema
// ============================================================================

export const AuthErrorResponseSchema = z.object({
  status: z.literal('error'),
  code: z.enum(['EMAIL_EXISTS', 'VALIDATION_ERROR', 'INVALID_INPUT', 'INVALID_CREDENTIALS', 'UNAUTHORIZED']),
  message: z.string(),
  details: z.array(z.object({
    field: z.string(),
    message: z.string(),
  })).optional(),
})

export type AuthErrorResponse = z.infer<typeof AuthErrorResponseSchema>
