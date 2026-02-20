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
    // Session cookie exists, allow access
    return NextResponse.next();
  }

  // Redirect authenticated users away from auth pages
  if (pathname.startsWith('/sign-in') || pathname.startsWith('/sign-up')) {
    if (sessionToken) {
      // Valid session cookie exists, redirect to dashboard
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard', '/dashboard/:path*', '/sign-in', '/sign-up'],
};
