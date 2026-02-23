/**
 * Tests: Next.js Middleware — route protection logic
 * Verifies redirect behaviour for protected and auth routes.
 */
import { describe, it, expect, vi } from "vitest";
import { middleware } from "@/middleware";
import { NextRequest, NextResponse } from "next/server";

// Helper to build a fake NextRequest
function makeRequest(
  pathname: string,
  cookies: Record<string, string> = {}
): NextRequest {
  const url = `http://localhost:3000${pathname}`;
  const request = new NextRequest(url);

  // Attach cookies
  Object.entries(cookies).forEach(([name, value]) => {
    request.cookies.set(name, value);
  });

  return request;
}

const SESSION_COOKIE = "better-auth.session_token";
const FAKE_TOKEN = "session-token-abc";

describe("Middleware: Route Protection", () => {
  describe("Unauthenticated user", () => {
    it("redirects /chatbot to /signin", async () => {
      const request = makeRequest("/chatbot");
      const response = await middleware(request);

      expect(response).toBeInstanceOf(NextResponse);
      const location = response.headers.get("location");
      expect(location).toContain("/signin");
    });

    it("redirects /analytics to /signin", async () => {
      const request = makeRequest("/analytics");
      const response = await middleware(request);

      const location = response.headers.get("location");
      expect(location).toContain("/signin");
    });

    it("redirects /settings to /signin", async () => {
      const request = makeRequest("/settings");
      const response = await middleware(request);

      const location = response.headers.get("location");
      expect(location).toContain("/signin");
    });

    it("includes callbackUrl in redirect query string", async () => {
      const request = makeRequest("/chatbot");
      const response = await middleware(request);

      const location = response.headers.get("location") ?? "";
      expect(location).toContain("callbackUrl=%2Fchatbot");
    });

    it("allows access to /signin without redirect", async () => {
      const request = makeRequest("/signin");
      const response = await middleware(request);

      // Should pass through (NextResponse.next())
      expect(response.status).toBe(200);
    });

    it("allows access to /signup without redirect", async () => {
      const request = makeRequest("/signup");
      const response = await middleware(request);

      expect(response.status).toBe(200);
    });
  });

  describe("Authenticated user", () => {
    it("allows access to /chatbot", async () => {
      const request = makeRequest("/chatbot", {
        [SESSION_COOKIE]: FAKE_TOKEN,
      });
      const response = await middleware(request);

      expect(response.status).toBe(200);
    });

    it("redirects /signin to /chatbot", async () => {
      const request = makeRequest("/signin", {
        [SESSION_COOKIE]: FAKE_TOKEN,
      });
      const response = await middleware(request);

      const location = response.headers.get("location");
      expect(location).toContain("/chatbot");
    });

    it("redirects /signup to /chatbot", async () => {
      const request = makeRequest("/signup", {
        [SESSION_COOKIE]: FAKE_TOKEN,
      });
      const response = await middleware(request);

      const location = response.headers.get("location");
      expect(location).toContain("/chatbot");
    });
  });
});
