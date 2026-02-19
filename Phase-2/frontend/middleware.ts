/**
 * Middleware for route protection
 *
 * @spec specs/003-todo-frontend/spec.md (FR-009)
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for Better Auth session cookie
  const sessionToken = request.cookies.get('better-auth.session_token')?.value;

  // Protect dashboard routes - require valid session
  if (pathname.startsWith('/dashboard')) {
    if (!sessionToken) {
      return NextResponse.redirect(new URL('/sign-in', request.url));
    }

    // Validate session by calling the session endpoint
    try {
      const response = await fetch(new URL('/api/auth/get-session', request.url), {
        headers: {
          cookie: request.headers.get('cookie') || '',
        },
      });

      if (!response.ok) {
        // Session invalid, redirect to sign-in
        return NextResponse.redirect(new URL('/sign-in', request.url));
      }
    } catch {
      // If validation fails, redirect to sign-in
      return NextResponse.redirect(new URL('/sign-in', request.url));
    }
  }

  // Redirect authenticated users away from auth pages
  if (pathname.startsWith('/sign-in') || pathname.startsWith('/sign-up')) {
    if (sessionToken) {
      // Validate session before redirecting
      try {
        const response = await fetch(new URL('/api/auth/get-session', request.url), {
          headers: {
            cookie: request.headers.get('cookie') || '',
          },
        });

        if (response.ok) {
          // Valid session, redirect to dashboard
          return NextResponse.redirect(new URL('/dashboard', request.url));
        }
      } catch {
        // Session validation failed, allow access to auth pages
      }
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard', '/dashboard/:path*', '/sign-in', '/sign-up'],
};
