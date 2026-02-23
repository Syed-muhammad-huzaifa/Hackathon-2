import { ApiError } from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    credentials: "include",
    headers,
  });

  if (!response.ok) {
    let errorData: { code?: string; message?: string } = {};
    try {
      errorData = await response.json();
    } catch {
      // fallback
    }
    throw new ApiError(
      errorData.code ?? "UNKNOWN_ERROR",
      errorData.message ?? response.statusText,
      response.status
    );
  }

  return response.json() as Promise<T>;
}
