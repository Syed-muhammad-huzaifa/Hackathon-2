import { authClient } from "@/lib/auth/auth-client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, unknown>;
  result?: unknown;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls?: ToolCall[];
}

export interface TaskItem {
  id: string;
  title: string;
  status: "pending" | "in_progress" | "completed";
}

export interface TaskStats {
  tasks: TaskItem[];
  total: number;
  completed: number;
  pending: number;
  inProgress: number;
}

// Token cache with 1-minute buffer before expiration
let cachedToken: string | null = null;
let tokenExpiry: number = 0;

class ChatAPIClient {
  private async getAuthToken(): Promise<string> {
    const now = Date.now();

    // Return cached token if still valid (with 1-minute buffer)
    if (cachedToken && tokenExpiry > now + 60000) {
      return cachedToken;
    }

    // Get new JWT token from Better Auth
    const result = await authClient.token();

    // Check for error
    if ("error" in result && result.error) {
      throw new Error("Failed to get authentication token");
    }

    // Extract token from data
    const tokenData = "data" in result ? result.data : result;

    if (!tokenData?.token) {
      throw new Error("No token in response");
    }

    // Cache token (JWT tokens typically expire in 7 days for Better Auth)
    cachedToken = tokenData.token;
    tokenExpiry = now + (7 * 24 * 60 * 60 * 1000); // 7 days

    return tokenData.token;
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = await this.getAuthToken();

    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
  }

  private async getUserId(): Promise<string> {
    const session = await authClient.getSession();

    if (!session?.data?.user?.id) {
      throw new Error("User not found in session");
    }

    return session.data.user.id;
  }

  async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    const userId = await this.getUserId();
    const headers = await this.getAuthHeaders();

    const body: ChatRequest = {
      message,
      ...(conversationId && { conversation_id: conversationId }),
    };

    const response = await fetch(`${API_URL}/api/${userId}/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Chat API error: ${error}`);
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string; database: string }> {
    const response = await fetch(`${API_URL}/health/ready`);

    if (!response.ok) {
      throw new Error("Backend health check failed");
    }

    return response.json();
  }

  async fetchTaskStats(): Promise<TaskStats> {
    const userId = await this.getUserId();
    const headers = await this.getAuthHeaders();

    const response = await fetch(`${API_URL}/api/${userId}/tasks`, { headers });

    if (!response.ok) {
      throw new Error(`Tasks API error: ${response.statusText}`);
    }

    return response.json();
  }

  async fetchCompletedTasks(): Promise<TaskItem[]> {
    const userId = await this.getUserId();
    const headers = await this.getAuthHeaders();

    const response = await fetch(
      `${API_URL}/api/${userId}/tasks?status=completed`,
      { headers }
    );

    if (!response.ok) {
      throw new Error(`Tasks API error: ${response.statusText}`);
    }

    const data: TaskStats = await response.json();
    return data.tasks;
  }
}

export const chatAPI = new ChatAPIClient();
