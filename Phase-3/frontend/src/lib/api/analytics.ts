import type { Task } from "@/types";
import { apiClient } from "./client";

export async function getUserTasks(
  userId: string,
  token: string
): Promise<Task[]> {
  return apiClient<Task[]>(
    `/api/${userId}/tasks`,
    { method: "GET" },
    token
  );
}
