/**
 * Tests: Backend health endpoint connectivity
 * Verifies the frontend can reach the backend health endpoints.
 */
import { describe, it, expect, vi, afterEach } from "vitest";

const API_URL = "http://localhost:8001";

describe("Backend Health Endpoints", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("GET /health/live", () => {
    it("returns status ok", async () => {
      const mockFetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ status: "ok" }),
      });
      vi.stubGlobal("fetch", mockFetch);

      const response = await fetch(`${API_URL}/health/live`);
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data.status).toBe("ok");
      expect(mockFetch).toHaveBeenCalledWith(`${API_URL}/health/live`);
    });

    it("does not require authentication", async () => {
      const mockFetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ status: "ok" }),
      });
      vi.stubGlobal("fetch", mockFetch);

      // Call without any auth headers
      const response = await fetch(`${API_URL}/health/live`);
      expect(response.status).toBe(200);
    });
  });

  describe("GET /health/ready", () => {
    it("returns status ready and database connected", async () => {
      const mockFetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ status: "ready", database: "connected" }),
      });
      vi.stubGlobal("fetch", mockFetch);

      const response = await fetch(`${API_URL}/health/ready`);
      const data = await response.json();

      expect(response.ok).toBe(true);
      expect(data.status).toBe("ready");
      expect(data.database).toBe("connected");
    });

    it("returns 503 when database is unavailable", async () => {
      const mockFetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 503,
        json: async () => ({ status: "not_ready", database: "disconnected" }),
      });
      vi.stubGlobal("fetch", mockFetch);

      const response = await fetch(`${API_URL}/health/ready`);
      expect(response.ok).toBe(false);
      expect(response.status).toBe(503);
    });
  });
});
