import type { ChatRequest, ChatResponse } from "@/types";
import { apiClient } from "./client";

export async function sendChatMessage(
  userId: string,
  request: ChatRequest,
  token: string
): Promise<ChatResponse> {
  return apiClient<ChatResponse>(
    `/api/${userId}/chat`,
    {
      method: "POST",
      body: JSON.stringify(request),
    },
    token
  );
}
