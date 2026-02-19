/**
 * Session endpoint - returns current user session
 *
 * @spec specs/003-todo-frontend/spec.md (FR-003)
 */

import { auth } from '@/lib/auth/server';
import { headers } from 'next/headers';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session) {
      return NextResponse.json(
        { user: null, session: null },
        { status: 200 }
      );
    }

    return NextResponse.json({
      user: session.user,
      session: {
        id: session.session.id,
        expiresAt: session.session.expiresAt,
      },
    });
  } catch {
    return NextResponse.json(
      { error: 'Failed to fetch session' },
      { status: 500 }
    );
  }
}
