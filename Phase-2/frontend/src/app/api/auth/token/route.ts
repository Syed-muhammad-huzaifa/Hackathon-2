/**
 * JWT Token endpoint for backend API authentication
 *
 * Uses Better Auth JWT plugin to retrieve JWT token from session.
 *
 * @spec specs/003-todo-frontend/spec.md (FR-003, FR-036)
 */

import { auth } from '@/lib/auth/server';
import { headers } from 'next/headers';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Get current session from Better Auth
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session?.session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get JWT token using Better Auth JWT plugin
    // The JWT plugin adds a getToken method to the auth instance
    const tokenResponse = await auth.api.getToken({
      headers: await headers(),
    });

    if (!tokenResponse?.token) {
      return NextResponse.json(
        { error: 'No token available' },
        { status: 401 }
      );
    }

    return NextResponse.json({ token: tokenResponse.token });
  } catch {
    return NextResponse.json(
      { error: 'Failed to fetch token' },
      { status: 500 }
    );
  }
}
