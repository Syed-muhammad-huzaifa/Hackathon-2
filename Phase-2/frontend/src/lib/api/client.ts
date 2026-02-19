/**
 * Type-safe API client for backend communication
 *
 * Automatically injects JWT tokens from Better Auth for FastAPI backend authentication.
 *
 * @spec specs/003-todo-frontend/spec.md (FR-003, FR-036, FR-037)
 */

import { z } from 'zod'
import { authClient } from '@/lib/auth/client'

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// JWT Token Cache
let cachedToken: string | null = null
let tokenExpiresAt: number = 0

async function getJWTToken(): Promise<string | null> {
  // Return cached token if still valid (with 1 minute buffer)
  const now = Date.now()
  if (cachedToken && tokenExpiresAt > now + 60000) {
    return cachedToken
  }

  // Fetch new token using Better Auth JWT plugin
  try {
    const { data, error } = await authClient.token()

    if (error || !data?.token) {
      return null
    }

    cachedToken = data.token

    // Decode JWT to get expiration (tokens typically expire in 15 minutes)
    try {
      const payload = JSON.parse(atob(data.token.split('.')[1]))
      tokenExpiresAt = payload.exp * 1000 // Convert to milliseconds
    } catch {
      // If we can't decode, cache for 10 minutes
      tokenExpiresAt = now + 10 * 60 * 1000
    }

    return cachedToken
  } catch {
    return null
  }
}

// ============================================================================
// Error Classes
// ============================================================================

export class APIError extends Error {
  constructor(
    public status: number,
    public code: string,
    public details?: unknown
  ) {
    super(`API Error: ${code}`)
    this.name = 'APIError'
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'NetworkError'
  }
}

// ============================================================================
// API Client
// ============================================================================

interface RequestOptions extends RequestInit {
  skipAuth?: boolean
}

/**
 * Type-safe API client with automatic JWT injection and Zod validation
 *
 * @param endpoint - API endpoint path (e.g., '/auth/sign-in')
 * @param schema - Zod schema for response validation
 * @param options - Fetch options (method, body, headers, etc.)
 * @returns Parsed and validated response data
 *
 * @throws {APIError} When API returns error response
 * @throws {NetworkError} When network request fails
 * @throws {z.ZodError} When response doesn't match schema
 */
export async function apiClient<T>(
  endpoint: string,
  schema: z.ZodSchema<T>,
  options: RequestOptions = {}
): Promise<T> {
  const { skipAuth = false, ...fetchOptions } = options

  const url = `${API_BASE_URL}${endpoint}`

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
  }

  // Get JWT token from Better Auth session and add to Authorization header
  if (!skipAuth) {
    const token = await getJWTToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
    })

    // Parse response body
    const data = await response.json()

    // Handle error responses
    if (!response.ok) {
      throw new APIError(
        response.status,
        data.code || data.detail || 'UNKNOWN_ERROR',
        data.details
      )
    }

    // Validate and parse response with Zod
    return schema.parse(data)
  } catch (error) {
    // Re-throw API errors and Zod errors as-is
    if (error instanceof APIError || error instanceof z.ZodError) {
      throw error
    }

    // Network errors (fetch failed)
    if (error instanceof TypeError) {
      throw new NetworkError('Network request failed. Please check your connection.')
    }

    // Unknown errors
    throw new NetworkError('An unexpected error occurred')
  }
}

// ============================================================================
// Convenience Methods
// ============================================================================

/**
 * GET request
 */
export async function get<T>(
  endpoint: string,
  schema: z.ZodSchema<T>,
  options: RequestOptions = {}
): Promise<T> {
  return apiClient(endpoint, schema, {
    ...options,
    method: 'GET',
  })
}

/**
 * POST request
 */
export async function post<T>(
  endpoint: string,
  schema: z.ZodSchema<T>,
  body: unknown,
  options: RequestOptions = {}
): Promise<T> {
  return apiClient(endpoint, schema, {
    ...options,
    method: 'POST',
    body: JSON.stringify(body),
  })
}

/**
 * PATCH request
 */
export async function patch<T>(
  endpoint: string,
  schema: z.ZodSchema<T>,
  body: unknown,
  options: RequestOptions = {}
): Promise<T> {
  return apiClient(endpoint, schema, {
    ...options,
    method: 'PATCH',
    body: JSON.stringify(body),
  })
}

/**
 * DELETE request
 */
export async function del<T>(
  endpoint: string,
  schema: z.ZodSchema<T>,
  options: RequestOptions = {}
): Promise<T> {
  return apiClient(endpoint, schema, {
    ...options,
    method: 'DELETE',
  })
}

// ============================================================================
// Error Handling Utilities
// ============================================================================

/**
 * Check if error is an API error
 */
export function isAPIError(error: unknown): error is APIError {
  return error instanceof APIError
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: unknown): error is NetworkError {
  return error instanceof NetworkError
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: unknown): string {
  if (isAPIError(error)) {
    return error.code
  }

  if (isNetworkError(error)) {
    return error.message
  }

  if (error instanceof z.ZodError) {
    return 'Invalid response from server'
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'An unexpected error occurred'
}
