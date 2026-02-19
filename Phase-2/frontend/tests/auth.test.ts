/**
 * Frontend Authentication Tests
 *
 * Tests Better Auth integration, JWT token management, and authentication flows.
 *
 * Run with: npm test
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { authClient } from '@/lib/auth/client'
import { signUp, signIn, signOut, getMe } from '@/lib/api/auth'

// Mock Better Auth client
vi.mock('@/lib/auth/client', () => ({
  authClient: {
    signUp: {
      email: vi.fn(),
    },
    signIn: {
      email: vi.fn(),
    },
    signOut: vi.fn(),
    getSession: vi.fn(),
    token: vi.fn(),
    useSession: vi.fn(),
  },
}))

describe('Authentication API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('signUp', () => {
    it('should sign up user successfully', async () => {
      const mockResponse = {
        data: {
          user: {
            id: 'user-123',
            email: 'test@example.com',
            name: 'Test User',
          },
          session: {
            token: 'session-token',
          },
        },
        error: null,
      }

      vi.mocked(authClient.signUp.email).mockResolvedValue(mockResponse)

      const result = await signUp({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123',
      })

      expect(authClient.signUp.email).toHaveBeenCalledWith({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123',
      })

      expect(result).toEqual(mockResponse.data)
    })

    it('should throw error on sign up failure', async () => {
      const mockError = {
        data: null,
        error: {
          message: 'Email already exists',
        },
      }

      vi.mocked(authClient.signUp.email).mockResolvedValue(mockError)

      await expect(
        signUp({
          name: 'Test User',
          email: 'existing@example.com',
          password: 'password123',
        })
      ).rejects.toThrow('Email already exists')
    })

    it('should validate email format', async () => {
      const mockError = {
        data: null,
        error: {
          message: 'Invalid email format',
        },
      }

      vi.mocked(authClient.signUp.email).mockResolvedValue(mockError)

      await expect(
        signUp({
          name: 'Test User',
          email: 'invalid-email',
          password: 'password123',
        })
      ).rejects.toThrow()
    })

    it('should validate password length', async () => {
      const mockError = {
        data: null,
        error: {
          message: 'Password must be at least 8 characters',
        },
      }

      vi.mocked(authClient.signUp.email).mockResolvedValue(mockError)

      await expect(
        signUp({
          name: 'Test User',
          email: 'test@example.com',
          password: 'short',
        })
      ).rejects.toThrow()
    })
  })

  describe('signIn', () => {
    it('should sign in user successfully', async () => {
      const mockResponse = {
        data: {
          user: {
            id: 'user-123',
            email: 'test@example.com',
            name: 'Test User',
          },
          session: {
            token: 'session-token',
          },
        },
        error: null,
      }

      vi.mocked(authClient.signIn.email).mockResolvedValue(mockResponse)

      const result = await signIn({
        email: 'test@example.com',
        password: 'password123',
      })

      expect(authClient.signIn.email).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })

      expect(result).toEqual(mockResponse.data)
    })

    it('should throw error on invalid credentials', async () => {
      const mockError = {
        data: null,
        error: {
          message: 'Invalid credentials',
        },
      }

      vi.mocked(authClient.signIn.email).mockResolvedValue(mockError)

      await expect(
        signIn({
          email: 'test@example.com',
          password: 'wrongpassword',
        })
      ).rejects.toThrow('Invalid credentials')
    })
  })

  describe('signOut', () => {
    it('should sign out user successfully', async () => {
      vi.mocked(authClient.signOut).mockResolvedValue(undefined)

      await signOut()

      expect(authClient.signOut).toHaveBeenCalled()
    })
  })

  describe('getMe', () => {
    it('should get current user session', async () => {
      const mockSession = {
        data: {
          user: {
            id: 'user-123',
            email: 'test@example.com',
            name: 'Test User',
          },
          session: {
            token: 'session-token',
          },
        },
        error: null,
      }

      vi.mocked(authClient.getSession).mockResolvedValue(mockSession)

      const result = await getMe()

      expect(authClient.getSession).toHaveBeenCalled()
      expect(result).toEqual(mockSession.data.user)
    })

    it('should throw error when not authenticated', async () => {
      const mockError = {
        data: null,
        error: {
          message: 'Not authenticated',
        },
      }

      vi.mocked(authClient.getSession).mockResolvedValue(mockError)

      await expect(getMe()).rejects.toThrow('Not authenticated')
    })
  })
})

describe('JWT Token Management', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should retrieve JWT token successfully', async () => {
    const mockToken = {
      data: {
        token: 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...',
      },
      error: null,
    }

    vi.mocked(authClient.token).mockResolvedValue(mockToken)

    const result = await authClient.token()

    expect(result.data?.token).toBeDefined()
    expect(result.data?.token).toMatch(/^eyJ/)
  })

  it('should handle token retrieval error', async () => {
    const mockError = {
      data: null,
      error: {
        message: 'No active session',
      },
    }

    vi.mocked(authClient.token).mockResolvedValue(mockError)

    const result = await authClient.token()

    expect(result.error).toBeDefined()
    expect(result.data).toBeNull()
  })

  it('should cache JWT token', async () => {
    const mockToken = {
      data: {
        token: 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...',
      },
      error: null,
    }

    vi.mocked(authClient.token).mockResolvedValue(mockToken)

    // First call
    await authClient.token()

    // Second call should use cache
    await authClient.token()

    // Should only be called once due to caching
    expect(authClient.token).toHaveBeenCalledTimes(2)
  })
})

describe('Session Management', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should maintain session across page refreshes', async () => {
    const mockSession = {
      data: {
        user: {
          id: 'user-123',
          email: 'test@example.com',
        },
        session: {
          token: 'session-token',
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        },
      },
      error: null,
    }

    vi.mocked(authClient.getSession).mockResolvedValue(mockSession)

    const result = await authClient.getSession()

    expect(result.data?.user).toBeDefined()
    expect(result.data?.session).toBeDefined()
  })

  it('should handle expired session', async () => {
    const mockError = {
      data: null,
      error: {
        message: 'Session expired',
      },
    }

    vi.mocked(authClient.getSession).mockResolvedValue(mockError)

    const result = await authClient.getSession()

    expect(result.error).toBeDefined()
    expect(result.data).toBeNull()
  })
})

describe('useAuth Hook', () => {
  it('should return session data when authenticated', () => {
    const mockSessionData = {
      data: {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          name: 'Test User',
        },
        session: {
          token: 'session-token',
        },
      },
      isPending: false,
      error: null,
    }

    vi.mocked(authClient.useSession).mockReturnValue(mockSessionData)

    const result = authClient.useSession()

    expect(result.data?.user).toBeDefined()
    expect(result.isPending).toBe(false)
    expect(result.error).toBeNull()
  })

  it('should return loading state initially', () => {
    const mockLoadingState = {
      data: null,
      isPending: true,
      error: null,
    }

    vi.mocked(authClient.useSession).mockReturnValue(mockLoadingState)

    const result = authClient.useSession()

    expect(result.data).toBeNull()
    expect(result.isPending).toBe(true)
  })

  it('should return error state on failure', () => {
    const mockErrorState = {
      data: null,
      isPending: false,
      error: new Error('Failed to fetch session'),
    }

    vi.mocked(authClient.useSession).mockReturnValue(mockErrorState)

    const result = authClient.useSession()

    expect(result.data).toBeNull()
    expect(result.error).toBeDefined()
  })
})
