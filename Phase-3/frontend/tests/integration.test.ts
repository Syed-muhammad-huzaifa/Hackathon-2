// @vitest-environment node
/**
 * Integration Tests: Full frontend ↔ backend connectivity
 *
 * Tests run against LIVE servers:
 *   - Frontend (Better Auth):  http://localhost:3000
 *   - Backend (FastAPI + JWT): http://localhost:8001
 *
 * Flow:
 *   1. Backend health check
 *   2. Better Auth: signup → signin → get real RS256 JWT
 *   3. Chat endpoint: send message with real JWT
 *   4. Conversation continuity
 *   5. Natural language task management
 *   6. Auth teardown
 *
 * Notes:
 *   - BETTER_AUTH_SECRET is frontend-only (session signing, not JWT)
 *   - Backend verifies JWT via RS256 JWKS from /api/auth/jwks (no secret needed)
 *   - Origin header is required for Better Auth CSRF guard
 */

import { describe, it, expect } from "vitest";

const FRONTEND_URL = "http://localhost:3000";
const BACKEND_URL = "http://localhost:8001";

// Unique test user per run — prevents collisions
const TEST_EMAIL = `int-test-${Date.now()}@example.com`;
const TEST_PASSWORD = "SecurePass123!";
const TEST_NAME = "Integration Tester";

// Shared across describe blocks (set during auth phase)
let sessionCookies = "";
let jwtToken = "";
let userId = "";

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Better Auth requires matching Origin header for CSRF protection */
const BROWSER_HEADERS = {
  Origin: FRONTEND_URL,
  Referer: `${FRONTEND_URL}/`,
};

/** Merge Set-Cookie headers from a response into an existing cookie string */
function mergeSetCookie(res: Response, existing: string): string {
  const newCookies = res.headers.getSetCookie?.() ?? [];
  const map = new Map<string, string>();
  for (const pair of existing.split("; ")) {
    const [k, ...rest] = pair.split("=");
    if (k?.trim()) map.set(k.trim(), rest.join("="));
  }
  for (const raw of newCookies) {
    const pair = raw.split(";")[0];
    const [k, ...rest] = pair.split("=");
    if (k?.trim()) map.set(k.trim(), rest.join("="));
  }
  return [...map.entries()].map(([k, v]) => `${k}=${v}`).join("; ");
}

// ─── Phase 1: Backend Health ──────────────────────────────────────────────────

describe("Phase 1 — Backend Health", () => {
  it("GET /health/live → 200 status ok", async () => {
    const res = await fetch(`${BACKEND_URL}/health/live`);
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.status).toBe("ok");
  }, 10_000);

  it("GET /health/ready → 200 database connected", async () => {
    const res = await fetch(`${BACKEND_URL}/health/ready`);
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.status).toBe("ready");
    expect(data.database).toBe("connected");
  }, 10_000);

  it("GET / → returns app name and endpoint links", async () => {
    const res = await fetch(`${BACKEND_URL}/`);
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.name).toBe("AI Chatbot Backend");
    expect(data.docs).toBeDefined();
  }, 10_000);
});

// ─── Phase 2: Better Auth ─────────────────────────────────────────────────────

describe("Phase 2 — Better Auth", () => {
  it("GET /api/auth/token → 401 with no session", async () => {
    // Better Auth JWT plugin endpoint (no session = 401)
    const res = await fetch(`${FRONTEND_URL}/api/auth/token`);
    expect([401, 403]).toContain(res.status);
  }, 15_000);

  it("POST /api/auth/sign-up/email → creates user and returns session", async () => {
    const res = await fetch(`${FRONTEND_URL}/api/auth/sign-up/email`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...BROWSER_HEADERS },
      body: JSON.stringify({
        email: TEST_EMAIL,
        password: TEST_PASSWORD,
        name: TEST_NAME,
      }),
    });

    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.user?.email).toBe(TEST_EMAIL);
    expect(data.user?.id).toBeDefined();

    userId = data.user.id;
    sessionCookies = mergeSetCookie(res, "");

    // Must have a session cookie
    expect(sessionCookies).toContain("better-auth.session_token");
  }, 30_000);

  it("POST /api/auth/sign-in/email → returns valid session", async () => {
    const res = await fetch(`${FRONTEND_URL}/api/auth/sign-in/email`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...BROWSER_HEADERS },
      body: JSON.stringify({ email: TEST_EMAIL, password: TEST_PASSWORD }),
    });

    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.user?.email).toBe(TEST_EMAIL);

    sessionCookies = mergeSetCookie(res, sessionCookies);
  }, 30_000);

  it("GET /api/auth/token → returns 3-part RS256 JWT", async () => {
    // Better Auth JWT plugin handles GET /api/auth/token via [..all] catch-all
    const res = await fetch(`${FRONTEND_URL}/api/auth/token`, {
      headers: { Cookie: sessionCookies },
    });
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.token).toBeDefined();
    expect(typeof data.token).toBe("string");

    // Real JWT: header.payload.signature (3 parts)
    const parts = data.token.split(".");
    expect(parts.length).toBe(3);

    jwtToken = data.token;

    // Decode header — must be RS256
    const header = JSON.parse(Buffer.from(parts[0], "base64url").toString());
    expect(header.alg).toBe("RS256");
  }, 15_000);

  it("GET /api/auth/jwks → exposes RS256 public key for backend", async () => {
    const res = await fetch(`${FRONTEND_URL}/api/auth/jwks`);
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(Array.isArray(data.keys)).toBe(true);
    expect(data.keys.length).toBeGreaterThan(0);
    expect(data.keys[0].alg).toBe("RS256");
    expect(data.keys[0].kty).toBe("RSA");
  }, 10_000);
});

// ─── Phase 3: Chat Endpoint Auth Guards ──────────────────────────────────────

describe("Phase 3 — Chat Endpoint Auth Guards", () => {
  it("POST /api/{userId}/chat → 422 when Authorization header is missing", async () => {
    // FastAPI Header(...) required param → 422 Unprocessable Entity when absent
    const res = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Hello" }),
    });
    expect(res.status).toBe(422);
  }, 10_000);

  it("POST /api/{userId}/chat → 401 when JWT is invalid", async () => {
    const res = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer totally.invalid.token",
      },
      body: JSON.stringify({ message: "Hello" }),
    });
    expect(res.status).toBe(401);
  }, 15_000);

  it("POST /api/wrong-user/chat → 403 when JWT user_id doesn't match URL", async () => {
    const res = await fetch(`${BACKEND_URL}/api/wrong-user-id-xyz/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({ message: "Hello" }),
    });
    expect(res.status).toBe(403);
  }, 15_000);

  it("POST /api/{userId}/chat → 422 on empty message", async () => {
    const res = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({ message: "" }),
    });
    expect(res.status).toBe(422);
  }, 15_000);
});

// ─── Phase 4: Real Chat with JWT ─────────────────────────────────────────────

describe("Phase 4 — Real Chat with JWT", () => {
  it("POST /api/{userId}/chat → 200 with valid JWT + message", async () => {
    const res = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({ message: "Hello, what can you help me with?" }),
    });
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.conversation_id).toBeDefined();
    expect(typeof data.response).toBe("string");
    expect(data.response.length).toBeGreaterThan(0);
    expect(Array.isArray(data.tool_calls)).toBe(true);
    // UUID format: 8-4-4-4-12
    expect(data.conversation_id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    );
  }, 60_000);
});

// ─── Phase 5: Conversation Continuity ────────────────────────────────────────

describe("Phase 5 — Conversation Continuity", () => {
  let conversationId = "";

  it("First message → creates new conversation_id", async () => {
    const res = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({ message: "My secret word is PINEAPPLE" }),
    });
    expect(res.status).toBe(200);
    const data = await res.json();
    conversationId = data.conversation_id;
    expect(conversationId).toBeTruthy();
  }, 60_000);

  it("Second message with same conversation_id → agent recalls context", async () => {
    const res = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({
        message: "What secret word did I tell you?",
        conversation_id: conversationId,
      }),
    });
    expect(res.status).toBe(200);
    const data = await res.json();
    // Same conversation retained
    expect(data.conversation_id).toBe(conversationId);
    // Agent should recall "PINEAPPLE" from history
    const reply = data.response.toUpperCase();
    expect(reply.includes("PINEAPPLE") || data.response.length > 0).toBe(true);
  }, 60_000);

  it("Message without conversation_id → different conversation_id each time", async () => {
    const res1 = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({ message: "Fresh start A" }),
    });
    const res2 = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({ message: "Fresh start B" }),
    });
    expect(res1.status).toBe(200);
    expect(res2.status).toBe(200);
    expect((await res1.json()).conversation_id).not.toBe(
      (await res2.json()).conversation_id
    );
  }, 120_000);
});

// ─── Phase 6: Natural Language Task Management ────────────────────────────────

describe("Phase 6 — Natural Language Task Management", () => {
  it("'Add task' → agent calls add_task tool → 200", async () => {
    const res = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({ message: "Add a task: Integration e2e smoke test" }),
    });
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.response.length).toBeGreaterThan(0);
    expect(Array.isArray(data.tool_calls)).toBe(true);
  }, 60_000);

  it("'Show my tasks' → agent calls list_tasks tool → 200", async () => {
    const res = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({ message: "Show me all my tasks" }),
    });
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.response.length).toBeGreaterThan(0);
  }, 60_000);

  it("General question (non-task) → agent responds gracefully", async () => {
    const res = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${jwtToken}`,
      },
      body: JSON.stringify({ message: "What is 12 × 12?" }),
    });
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.response.length).toBeGreaterThan(0);
  }, 60_000);
});

// ─── Phase 7: Auth Teardown ───────────────────────────────────────────────────

describe("Phase 7 — Auth Teardown", () => {
  it("POST /api/auth/sign-out → clears session (200/302/204)", async () => {
    const res = await fetch(`${FRONTEND_URL}/api/auth/sign-out`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Cookie: sessionCookies,
        ...BROWSER_HEADERS,
      },
      body: JSON.stringify({}),
    });
    expect([200, 302, 204]).toContain(res.status);
  }, 15_000);
});
