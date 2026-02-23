/**
 * Tests: Better Auth configuration and client setup.
 */
import { describe, it, expect, vi } from "vitest";

// Mock the Drizzle DB connection (avoid real DB in unit tests)
vi.mock("@/lib/db", () => ({
  getDb: vi.fn(() => ({})),
  schema: {
    user: {},
    session: {},
    account: {},
    verification: {},
  },
}));

// Mock better-auth to avoid real database operations
vi.mock("better-auth", () => ({
  betterAuth: vi.fn((config) => ({
    _config: config,
    api: {
      getSession: vi.fn(),
    },
    $Infer: { Session: {} },
  })),
}));

vi.mock("better-auth/adapters/drizzle", () => ({
  drizzleAdapter: vi.fn(() => "mock-drizzle-adapter"),
}));

vi.mock("better-auth/plugins", () => ({
  jwt: vi.fn(() => ({ name: "jwt-plugin" })),
}));

describe("Better Auth Configuration", () => {
  it("creates auth instance without throwing", async () => {
    expect(async () => {
      await import("@/lib/auth/auth");
    }).not.toThrow();
  });

  it("exports auth object", async () => {
    const mod = await import("@/lib/auth/auth");
    expect(mod.auth).toBeDefined();
  });
});

describe("Better Auth Client", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it("creates auth client with jwtClient plugin", async () => {
    const createAuthClientMock = vi.fn(() => ({
      token: vi.fn(),
      getSession: vi.fn(),
      signIn: {
        email: vi.fn(),
      },
      signUp: {
        email: vi.fn(),
      },
      signOut: vi.fn(),
    }));

    vi.doMock("better-auth/react", () => ({
      createAuthClient: createAuthClientMock,
    }));
    vi.doMock("better-auth/client/plugins", () => ({
      jwtClient: vi.fn(() => ({ name: "jwt-client-plugin" })),
    }));

    const { authClient } = await import("@/lib/auth/auth-client");

    expect(authClient).toBeDefined();
    expect(createAuthClientMock).toHaveBeenCalledOnce();

    // Verify jwtClient plugin was passed
    const [config] = createAuthClientMock.mock.calls[0];
    expect(config.plugins).toBeDefined();
    expect(config.plugins).toHaveLength(1);
  });
});
