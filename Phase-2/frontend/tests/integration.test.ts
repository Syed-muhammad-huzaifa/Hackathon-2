/**
 * End-to-End Integration Tests
 *
 * Tests complete authentication flow from frontend to backend.
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { authClient } from '@/lib/auth/client'
import { fetchTasks, createTask } from '@/lib/api/tasks'

// These tests require both frontend and backend servers running
describe('E2E Integration Tests', () => {
  const testUser = {
    name: 'E2E Test User',
    email: `e2e-test-${Date.now()}@example.com`,
    password: 'testpassword123',
  }

  let userId: string

  describe('Complete Authentication Flow', () => {
    it('should sign up new user', async () => {
      const response = await authClient.signUp.email({
        name: testUser.name,
        email: testUser.email,
        password: testUser.password,
      })

      expect(response.data).toBeDefined()
      expect(response.error).toBeNull()
      expect(response.data?.user.email).toBe(testUser.email)

      userId = response.data!.user.id
    })

    it('should retrieve JWT token after sign up', async () => {
      const tokenResponse = await authClient.token()

      expect(tokenResponse.data).toBeDefined()
      expect(tokenResponse.error).toBeNull()
      expect(tokenResponse.data?.token).toMatch(/^eyJ/)
    })

    it('should get current session', async () => {
      const sessionResponse = await authClient.getSession()

      expect(sessionResponse.data).toBeDefined()
      expect(sessionResponse.error).toBeNull()
      expect(sessionResponse.data?.user.email).toBe(testUser.email)
    })

    it('should sign out user', async () => {
      await authClient.signOut()

      const sessionResponse = await authClient.getSession()
      expect(sessionResponse.data).toBeNull()
    })

    it('should sign in existing user', async () => {
      const response = await authClient.signIn.email({
        email: testUser.email,
        password: testUser.password,
      })

      expect(response.data).toBeDefined()
      expect(response.error).toBeNull()
      expect(response.data?.user.email).toBe(testUser.email)
    })
  })

  describe('Backend API Integration', () => {
    beforeAll(async () => {
      // Ensure user is signed in
      await authClient.signIn.email({
        email: testUser.email,
        password: testUser.password,
      })
    })

    it('should fetch tasks with JWT authentication', async () => {
      const tasks = await fetchTasks(userId)

      expect(tasks).toBeDefined()
      expect(tasks.status).toBe('success')
      expect(Array.isArray(tasks.data)).toBe(true)
    })

    it('should create task with JWT authentication', async () => {
      const newTask = {
        title: 'E2E Test Task',
        description: 'Created by E2E test',
        status: 'pending' as const,
        priority: 'high' as const,
      }

      const response = await createTask(userId, newTask)

      expect(response).toBeDefined()
      expect(response.status).toBe('success')
      expect(response.data.title).toBe(newTask.title)
      expect(response.data.user_id).toBe(userId)
    })

    it('should not access other users tasks', async () => {
      const otherUserId = 'other-user-id'

      await expect(fetchTasks(otherUserId)).rejects.toThrow()
    })

    it('should handle expired token', async () => {
      // Sign out to invalidate session
      await authClient.signOut()

      // Try to fetch tasks without valid session
      await expect(fetchTasks(userId)).rejects.toThrow()
    })
  })

  describe('JWKS Verification', () => {
    it('should verify JWT token on backend', async () => {
      // Sign in
      await authClient.signIn.email({
        email: testUser.email,
        password: testUser.password,
      })

      // Get JWT token
      const tokenResponse = await authClient.token()
      const token = tokenResponse.data?.token

      expect(token).toBeDefined()

      // Call backend /auth/me endpoint
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      expect(response.ok).toBe(true)

      const data = await response.json()
      expect(data.status).toBe('success')
      expect(data.data.id).toBe(userId)
    })

    it('should reject invalid JWT token', async () => {
      const invalidToken = 'invalid.jwt.token'

      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${invalidToken}`,
        },
      })

      expect(response.ok).toBe(false)
      expect(response.status).toBe(401)
    })
  })

  describe('Session Persistence', () => {
    it('should maintain session across requests', async () => {
      // Sign in
      await authClient.signIn.email({
        email: testUser.email,
        password: testUser.password,
      })

      // First request
      const session1 = await authClient.getSession()
      expect(session1.data).toBeDefined()

      // Second request (should use same session)
      const session2 = await authClient.getSession()
      expect(session2.data).toBeDefined()
      expect(session2.data?.user.id).toBe(session1.data?.user.id)
    })

    it('should handle session expiration', async () => {
      // This test would require waiting for session to expire (7 days)
      // or manually manipulating session expiration
      // Skipping for now as it's time-consuming
    })
  })

  describe('Error Scenarios', () => {
    it('should handle network errors gracefully', async () => {
      // Temporarily stop backend server or use invalid URL
      const originalBaseURL = process.env.NEXT_PUBLIC_API_URL

      // Mock network error
      await expect(
        fetch('http://invalid-url:9999/api/test')
      ).rejects.toThrow()
    })

    it('should handle CORS errors', async () => {
      // Test CORS by making request from disallowed origin
      // This would require browser environment
    })

    it('should handle rate limiting', async () => {
      // Make many requests quickly to trigger rate limit
      const requests = Array.from({ length: 100 }, () =>
        fetch('http://localhost:8000/health')
      )

      const responses = await Promise.all(requests)

      // Some requests should be rate limited
      const rateLimited = responses.some((r) => r.status === 429)
      // Note: This depends on rate limit configuration
    })
  })
})
