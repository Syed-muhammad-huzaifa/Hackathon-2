/**
 * Tests: ChatAPIClient — unit tests for request building, token injection,
 * error handling, and response parsing.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// ── Mocks ────────────────────────────────────────────────────────────────────

const mockToken = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1c2VyLTEyMyJ9.sig";
const mockUserId = "user-abc-123";
const mockConversationId = "550e8400-e29b-41d4-a716-446655440000";

const mockAuthClient = {
  token: vi.fn(),
  getSession: vi.fn(),
};

vi.mock("@/lib/auth/auth-client", () => ({
  authClient: mockAuthClient,
}));

// Re-import after mocks are set up
async function importClient() {
  // Reset module cache so the mock is picked up
  const mod = await import("@/lib/api/chat-api-client");
  return mod.chatAPI;
}

// ── Tests ────────────────────────────────────────────────────────────────────

describe("ChatAPIClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("getAuthToken", () => {
    it("fetches and returns a JWT token from Better Auth", async () => {
      mockAuthClient.token.mockResolvedValueOnce({
        data: { token: mockToken },
      });
      mockAuthClient.getSession.mockResolvedValueOnce({
        data: { user: { id: mockUserId } },
      });

      const fetchMock = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          conversation_id: mockConversationId,
          response: "Hello! How can I help?",
          tool_calls: [],
        }),
      });
      vi.stubGlobal("fetch", fetchMock);

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      const result = await chatAPI.sendMessage("Hello");

      // Verify token was fetched
      expect(mockAuthClient.token).toHaveBeenCalledOnce();
      // Verify Authorization header was set
      const callArgs = fetchMock.mock.calls[0];
      expect(callArgs[1].headers["Authorization"]).toBe(`Bearer ${mockToken}`);
    });

    it("throws when token is missing from Better Auth response", async () => {
      mockAuthClient.token.mockResolvedValueOnce({ data: {} });
      mockAuthClient.getSession.mockResolvedValueOnce({
        data: { user: { id: mockUserId } },
      });

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      await expect(chatAPI.sendMessage("Hello")).rejects.toThrow(
        "No token in response"
      );
    });

    it("throws when Better Auth returns an error", async () => {
      mockAuthClient.token.mockResolvedValueOnce({
        error: { message: "Unauthorized" },
      });
      mockAuthClient.getSession.mockResolvedValueOnce({
        data: { user: { id: mockUserId } },
      });

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      await expect(chatAPI.sendMessage("Hello")).rejects.toThrow(
        "Failed to get authentication token"
      );
    });
  });

  describe("sendMessage", () => {
    it("sends POST to /api/{userId}/chat with correct body", async () => {
      vi.resetModules();
      mockAuthClient.token.mockResolvedValue({ data: { token: mockToken } });
      mockAuthClient.getSession.mockResolvedValue({
        data: { user: { id: mockUserId } },
      });

      const mockResponse = {
        conversation_id: mockConversationId,
        response: "Task added!",
        tool_calls: [{ name: "add_task", arguments: { title: "Buy milk" } }],
      };

      const fetchMock = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });
      vi.stubGlobal("fetch", fetchMock);

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      const result = await chatAPI.sendMessage("Add task: Buy milk");

      expect(result.conversation_id).toBe(mockConversationId);
      expect(result.response).toBe("Task added!");
      expect(result.tool_calls).toHaveLength(1);

      // Verify request details
      const [url, options] = fetchMock.mock.calls[0];
      expect(url).toBe(`http://localhost:8001/api/${mockUserId}/chat`);
      expect(options.method).toBe("POST");
      const body = JSON.parse(options.body);
      expect(body.message).toBe("Add task: Buy milk");
    });

    it("includes conversation_id in body when provided", async () => {
      vi.resetModules();
      mockAuthClient.token.mockResolvedValue({ data: { token: mockToken } });
      mockAuthClient.getSession.mockResolvedValue({
        data: { user: { id: mockUserId } },
      });

      const fetchMock = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          conversation_id: mockConversationId,
          response: "Got it",
          tool_calls: [],
        }),
      });
      vi.stubGlobal("fetch", fetchMock);

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      await chatAPI.sendMessage("Continue", mockConversationId);

      const [, options] = fetchMock.mock.calls[0];
      const body = JSON.parse(options.body);
      expect(body.conversation_id).toBe(mockConversationId);
    });

    it("does NOT include conversation_id when not provided", async () => {
      vi.resetModules();
      mockAuthClient.token.mockResolvedValue({ data: { token: mockToken } });
      mockAuthClient.getSession.mockResolvedValue({
        data: { user: { id: mockUserId } },
      });

      const fetchMock = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          conversation_id: "new-id-xyz",
          response: "Fresh start",
          tool_calls: [],
        }),
      });
      vi.stubGlobal("fetch", fetchMock);

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      await chatAPI.sendMessage("Hello");

      const [, options] = fetchMock.mock.calls[0];
      const body = JSON.parse(options.body);
      expect(body.conversation_id).toBeUndefined();
    });

    it("throws descriptive error on non-OK backend response", async () => {
      vi.resetModules();
      mockAuthClient.token.mockResolvedValue({ data: { token: mockToken } });
      mockAuthClient.getSession.mockResolvedValue({
        data: { user: { id: mockUserId } },
      });

      const fetchMock = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 403,
        text: async () => "Forbidden",
      });
      vi.stubGlobal("fetch", fetchMock);

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      await expect(chatAPI.sendMessage("Hello")).rejects.toThrow(
        "Chat API error: Forbidden"
      );
    });

    it("throws when user session is missing", async () => {
      vi.resetModules();
      mockAuthClient.getSession.mockResolvedValue({ data: null });

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      await expect(chatAPI.sendMessage("Hello")).rejects.toThrow(
        "User not found in session"
      );
    });
  });

  describe("healthCheck", () => {
    it("returns health status from backend", async () => {
      vi.resetModules();
      const fetchMock = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: "ready", database: "connected" }),
      });
      vi.stubGlobal("fetch", fetchMock);

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      const result = await chatAPI.healthCheck();

      expect(result.status).toBe("ready");
      expect(result.database).toBe("connected");
      expect(fetchMock).toHaveBeenCalledWith("http://localhost:8001/health/ready");
    });

    it("throws on backend health check failure", async () => {
      vi.resetModules();
      const fetchMock = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 503,
      });
      vi.stubGlobal("fetch", fetchMock);

      const { chatAPI } = await import("@/lib/api/chat-api-client");
      await expect(chatAPI.healthCheck()).rejects.toThrow(
        "Backend health check failed"
      );
    });
  });
});
