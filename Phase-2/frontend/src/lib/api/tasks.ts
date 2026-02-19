/**
 * Task API service
 *
 * @spec specs/003-todo-frontend/spec.md (FR-015, FR-016, FR-017, FR-020, FR-024)
 */

import { get, post, patch, del } from './client';
import {
  TaskListResponseSchema,
  TaskSingleResponseSchema,
  TaskDeleteResponseSchema,
  type TaskCreateRequest,
  type TaskUpdateRequest,
  type TaskListResponse,
  type TaskSingleResponse,
  type TaskDeleteResponse,
} from '@/lib/schemas/task';

/**
 * Fetch all tasks for the authenticated user
 */
export async function fetchTasks(userId: string): Promise<TaskListResponse> {
  return get(`/api/${userId}/tasks`, TaskListResponseSchema);
}

/**
 * Fetch a single task by ID
 */
export async function fetchTask(userId: string, taskId: string): Promise<TaskSingleResponse> {
  return get(`/api/${userId}/tasks/${taskId}`, TaskSingleResponseSchema);
}

/**
 * Create a new task
 */
export async function createTask(
  userId: string,
  data: TaskCreateRequest
): Promise<TaskSingleResponse> {
  return post(`/api/${userId}/tasks`, TaskSingleResponseSchema, data);
}

/**
 * Update an existing task
 */
export async function updateTask(
  userId: string,
  taskId: string,
  data: TaskUpdateRequest
): Promise<TaskSingleResponse> {
  return patch(`/api/${userId}/tasks/${taskId}`, TaskSingleResponseSchema, data);
}

/**
 * Delete a task
 */
export async function deleteTask(
  userId: string,
  taskId: string
): Promise<TaskDeleteResponse> {
  return del(`/api/${userId}/tasks/${taskId}`, TaskDeleteResponseSchema);
}
