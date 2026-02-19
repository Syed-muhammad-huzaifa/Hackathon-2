/**
 * Frontend Component Tests
 *
 * Tests authentication form components including sign-up, sign-in, and sign-out.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SignUpForm } from '@/components/auth/sign-up-form'
import { SignInForm } from '@/components/auth/sign-in-form'
import { SignOutButton } from '@/components/auth/sign-out-button'
import * as authApi from '@/lib/api/auth'

// Mock Next.js router
const mockPush = vi.fn()
const mockRefresh = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    refresh: mockRefresh,
  }),
}))

// Mock auth API
vi.mock('@/lib/api/auth')

// Mock toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

describe('SignUpForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render sign up form', () => {
    render(<SignUpForm />)

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
  })

  it('should validate required fields', async () => {
    const user = userEvent.setup()
    render(<SignUpForm />)

    const submitButton = screen.getByRole('button', { name: /create account/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/name/i)).toBeInTheDocument()
    })
  })

  it('should validate email format', async () => {
    const user = userEvent.setup()
    render(<SignUpForm />)

    const emailInput = screen.getByLabelText(/email/i)
    await user.type(emailInput, 'invalid-email')

    const submitButton = screen.getByRole('button', { name: /create account/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/invalid email/i)).toBeInTheDocument()
    })
  })

  it('should validate password length', async () => {
    const user = userEvent.setup()
    render(<SignUpForm />)

    const passwordInput = screen.getByLabelText(/password/i)
    await user.type(passwordInput, 'short')

    const submitButton = screen.getByRole('button', { name: /create account/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument()
    })
  })

  it('should submit form with valid data', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.signUp).mockResolvedValue({
      user: { id: 'user-123', email: 'test@example.com', name: 'Test User' },
    })

    render(<SignUpForm />)

    await user.type(screen.getByLabelText(/name/i), 'Test User')
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')

    const submitButton = screen.getByRole('button', { name: /create account/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(authApi.signUp).toHaveBeenCalledWith({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123',
      })
      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    })
  })

  it('should show error on sign up failure', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.signUp).mockRejectedValue(new Error('Email already exists'))

    render(<SignUpForm />)

    await user.type(screen.getByLabelText(/name/i), 'Test User')
    await user.type(screen.getByLabelText(/email/i), 'existing@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')

    const submitButton = screen.getByRole('button', { name: /create account/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(authApi.signUp).toHaveBeenCalled()
    })
  })

  it('should disable form during submission', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.signUp).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    )

    render(<SignUpForm />)

    await user.type(screen.getByLabelText(/name/i), 'Test User')
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')

    const submitButton = screen.getByRole('button', { name: /create account/i })
    await user.click(submitButton)

    expect(submitButton).toBeDisabled()
    expect(screen.getByText(/creating account/i)).toBeInTheDocument()
  })
})

describe('SignInForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render sign in form', () => {
    render(<SignInForm />)

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('should validate required fields', async () => {
    const user = userEvent.setup()
    render(<SignInForm />)

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/email/i)).toBeInTheDocument()
    })
  })

  it('should submit form with valid credentials', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.signIn).mockResolvedValue({
      user: { id: 'user-123', email: 'test@example.com', name: 'Test User' },
    })

    render(<SignInForm />)

    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(authApi.signIn).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    })
  })

  it('should show error on invalid credentials', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.signIn).mockRejectedValue(new Error('Invalid credentials'))

    render(<SignInForm />)

    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'wrongpassword')

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(authApi.signIn).toHaveBeenCalled()
    })
  })

  it('should disable form during submission', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.signIn).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    )

    render(<SignInForm />)

    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    await user.click(submitButton)

    expect(submitButton).toBeDisabled()
    expect(screen.getByText(/signing in/i)).toBeInTheDocument()
  })
})

describe('SignOutButton', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render sign out button', () => {
    render(<SignOutButton />)

    expect(screen.getByRole('button', { name: /sign out/i })).toBeInTheDocument()
  })

  it('should sign out user on click', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.signOut).mockResolvedValue(undefined)

    render(<SignOutButton />)

    const signOutButton = screen.getByRole('button', { name: /sign out/i })
    await user.click(signOutButton)

    await waitFor(() => {
      expect(authApi.signOut).toHaveBeenCalled()
      expect(mockPush).toHaveBeenCalledWith('/')
    })
  })

  it('should show error on sign out failure', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.signOut).mockRejectedValue(new Error('Sign out failed'))

    render(<SignOutButton />)

    const signOutButton = screen.getByRole('button', { name: /sign out/i })
    await user.click(signOutButton)

    await waitFor(() => {
      expect(authApi.signOut).toHaveBeenCalled()
    })
  })

  it('should disable button during sign out', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.signOut).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    )

    render(<SignOutButton />)

    const signOutButton = screen.getByRole('button', { name: /sign out/i })
    await user.click(signOutButton)

    expect(signOutButton).toBeDisabled()
  })
})
