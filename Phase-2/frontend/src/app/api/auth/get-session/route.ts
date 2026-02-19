/**
 * Get current JWT token for backend API calls
 *
 * @spec specs/003-todo-frontend/spec.md (FR-007)
 */

import { auth } from "@/lib/auth/server";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.session) {
      return NextResponse.json(
        { error: "Not authenticated" },
        { status: 401 }
      );
    }

    // Get JWT token from Better Auth
    const jwtToken = await auth.api.getToken({
      headers: request.headers,
    });

    if (!jwtToken) {
      return NextResponse.json(
        { error: "Failed to get JWT token" },
        { status: 500 }
      );
    }

    // Return the JWT token that can be sent to the backend
    return NextResponse.json({
      session: {
        token: jwtToken,
      },
    });
  } catch {
    return NextResponse.json(
      { error: "Failed to get session" },
      { status: 500 }
    );
  }
}
