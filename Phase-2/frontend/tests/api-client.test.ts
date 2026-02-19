/**
 * Frontend API Client Tests
 *
 * Tests API client functionality including JWT injection, error handling,
 * and integration with backend.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { apiClient, get, post, patch, del, APIError, NetworkError, getErrorMessage } from '@/lib/api/client'
import { authClient } from '@/lib/auth/client'
import { z } from 'zod'

// Mock fetch
global.fetch = vi.fn()

// Mock auth client
vi.mock('@/lib/auth/client', () => ({
  authClient: {
    token: vi.fn(),
  },
}))

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('JWT Token Injection', () => {
    it('should inject JWT token in Authorization header', async () => {
      const mockToken = {
        data: {
          token: 'test-jwt-token',
        },
        error: null,
      }

      vi.mocked(authClient.token).mockResolvedValue(mockToken)

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'test' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await apiClient('/test', schema)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-jwt-token',
          }),
        })
      )
    })

    it('should skip auth when skipAuth is true', async () => {
      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'test' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await apiClient('/test', schema, { skipAuth: true })

      expect(authClient.token).not.toHaveBeenCalled()
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.not.objectContaining({
          headers: expect.objectContaining({
            'Authorization': expect.anything(),
          }),
        })
      )
    })

    it('should handle missing token gracefully', async () => {
      vi.mocked(authClient.token).mockResolvedValue({
        data: null,
        error: { message: 'No session' },
      })

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'test' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await apiClient('/test', schema)

      // Should still make request without token
      expect(fetch).toHaveBeenCalled()
    })
  })

  describe('HTTP Methods', () => {
    it('should make GET request', async () => {
      vi.mocked(authClient.token).mockResolvedValue({
        data: { token: 'test-token' },
        error: null,
      })

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'test' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await get('/test', schema)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'GET',
        })
      )
    })

    it('should make POST request with body', async () => {
      vi.mocked(authClient.token).mockResolvedValue({
        data: { token: 'test-token' },
        error: null,
      })

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'created' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await post('/test', schema, { name: 'test' })

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'test' }),
        })
      )
    })

    it('should make PATCH request', async () => {
      vi.mocked(authClient.token).mockResolvedValue({
        data: { token: 'test-token' },
        error: null,
      })

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'updated' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await patch('/test', schema, { name: 'updated' })

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'PATCH',
        })
      )
    })

    it('should make DELETE request', async () => {
      vi.mocked(authClient.token).mockResolvedValue({
        data: { token: 'test-token' },
        error: null,
      })

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'deleted' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await del('/test', schema)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'DELETE',
        })
      )
    })
  })

  describe('Error Handling', () => {
    it('should throw APIError on 4xx response', async () => {
      vi.mocked(authClient.token).mockResolvedValue({
        data: { token: 'test-token' },
        error: null,
      })

      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ code: 'BAD_REQUEST', detail: 'Invalid input' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await expect(get('/test', schema)).rejects.toThrow(APIError)
    })

    it('should throw APIError on 401 Unauthorized', async () => {
      vi.mocked(authClient.token).mockResolvedValue({
        data: { token: 'invalid-token' },
        error: null,
      })

      vi.mocked(fetch).mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await expect(get('/test', schema)).rejects.toThrow(APIError)
    })

    it('should throw NetworkError on fetch failure', async () => {
      vi.mocked(authClient.token).mockResolvedValue({
        data: { token: 'test-token' },
        error: null,
      })

      vi.mocked(fetch).mockRejectedValue(new TypeError('Network error'))

      const schema = z.object({ data: z.string() })

      await expect(get('/test', schema)).rejects.toThrow(NetworkError)
    })

    it('should throw ZodError on invalid response schema', async () => {
      vi.mocked(authClient.token).mockResolvedValue({
        data: { token: 'test-token' },
        error: null,
      })

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ wrong: 'schema' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      await expect(get('/test', schema)).rejects.toThrow()
    })
  })

  describe('Error Message Helpers', () => {
    it('should get message from APIError', () => {
      const error = new APIError(400, 'BAD_REQUEST')
      expect(getErrorMessage(error)).toBe('BAD_REQUEST')
    })

    it('should get message from NetworkError', () => {
      const error = new NetworkError('Connection failed')
      expect(getErrorMessage(error)).toBe('Connection failed')
    })

    it('should get message from generic Error', () => {
      const error = new Error('Something went wrong')
      expect(getErrorMessage(error)).toBe('Something went wrong')
    })

    it('should return default message for unknown error', () => {
      const error = 'string error'
      expect(getErrorMessage(error)).toBe('An unexpected error occurred')
    })
  })

  describe('Token Caching', () => {
    it('should cache JWT token for 10 minutes', async () => {
      const mockToken = {
        data: {
          token: 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImV4cCI6OTk5OTk5OTk5OX0.signature',
        },
        error: null,
      }

      vi.mocked(authClient.token).mockResolvedValue(mockToken)

      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ data: 'test' }),
      } as Response)

      const schema = z.object({ data: z.string() })

      // First request
      await get('/test1', schema)

      // Second request (should use cached token)
      await get('/test2', schema)

      // Token should only be fetched once
      expect(authClient.token).toHaveBeenCalledTimes(1)
    })
  })
})

describe('Task API Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should fetch tasks with authentication', async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: 'test-token' },
      error: null,
    })

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        status: 'success',
        data: [
          {
            id: '123e4567-e89b-12d3-a456-426614174000',
            user_id: 'user-123',
            title: 'Task 1',
            description: 'Description 1',
            status: 'pending',
            priority: 'medium',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
          {
            id: '123e4567-e89b-12d3-a456-426614174001',
            user_id: 'user-123',
            title: 'Task 2',
            description: 'Description 2',
            status: 'completed',
            priority: 'high',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        ],
        meta: { total: 2 },
      }),
    } as Response)

    const { fetchTasks } = await import('@/lib/api/tasks')
    const tasks = await fetchTasks('user-123')

    expect(tasks.data).toHaveLength(2)
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/user-123/tasks',
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': 'Bearer test-token',
        }),
      })
    )
  })

  it('should create task with authentication', async () => {
    vi.mocked(authClient.token).mockResolvedValue({
      data: { token: 'test-token' },
      error: null,
    })

    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        status: 'success',
        data: {
          id: '123e4567-e89b-12d3-a456-426614174000',
          user_id: 'user-123',
          title: 'New Task',
          description: 'Description',
          status: 'pending',
          priority: 'high',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      }),
    } as Response)

    const { createTask } = await import('@/lib/api/tasks')
    const task = await createTask('user-123', {
      title: 'New Task',
      description: 'Description',
      priority: 'high',
    })

    expect(task.data.title).toBe('New Task')
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/user-123/tasks',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Authorization': 'Bearer test-token',
        }),
      })
    )
  })
})
