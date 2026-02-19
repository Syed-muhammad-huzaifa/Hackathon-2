/**
 * Task API contracts
 *
 * @spec specs/003-todo-frontend/spec.md (FR-015, FR-016, FR-017, FR-020, FR-024)
 */

import { z } from 'zod'

// ============================================================================
// Types
// ============================================================================

export type TaskStatus = z.infer<typeof TaskStatusSchema>
export type TaskPriority = z.infer<typeof TaskPrioritySchema>
export type Task = z.infer<typeof TaskSchema>
export type TaskCreateRequest = z.infer<typeof TaskCreateRequestSchema>
export type TaskUpdateRequest = z.infer<typeof TaskUpdateRequestSchema>
export type TaskListResponse = z.infer<typeof TaskListResponseSchema>
export type TaskSingleResponse = z.infer<typeof TaskSingleResponseSchema>
export type TaskDeleteResponse = z.infer<typeof TaskDeleteResponseSchema>

// ============================================================================
// Zod Schemas
// ============================================================================

export const TaskStatusSchema = z.enum(['pending', 'in-progress', 'completed', 'deleted'])

export const TaskPrioritySchema = z.enum(['low', 'medium', 'high'])

export const TaskSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string(),
  title: z.string().min(1).max(500),
  description: z.string().max(10000).nullable(),
  status: TaskStatusSchema,
  priority: TaskPrioritySchema,
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

export const TaskCreateRequestSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(500, 'Title must be less than 500 characters')
    .transform(val => val.trim()),
  description: z.string()
    .max(10000, 'Description must be less than 10,000 characters')
    .transform(val => val.trim())
    .optional(),
  priority: TaskPrioritySchema.default('medium'),
})

export const TaskUpdateRequestSchema = z.object({
  title: z.string()
    .min(1, 'Title cannot be empty')
    .max(500, 'Title must be less than 500 characters')
    .transform(val => val.trim())
    .optional(),
  description: z.string()
    .max(10000, 'Description must be less than 10,000 characters')
    .transform(val => val.trim())
    .optional(),
  status: TaskStatusSchema.optional(),
  priority: TaskPrioritySchema.optional(),
})

export const TaskListResponseSchema = z.object({
  status: z.literal('success'),
  data: z.array(TaskSchema),
  meta: z.object({
    total: z.number(),
  }),
})

export const TaskSingleResponseSchema = z.object({
  status: z.literal('success'),
  data: TaskSchema,
  message: z.string().optional(),
})

export const TaskDeleteResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string(),
})

// ============================================================================
// Error Response Schema
// ============================================================================

export const TaskErrorResponseSchema = z.object({
  status: z.literal('error'),
  code: z.enum([
    'VALIDATION_ERROR',
    'NOT_FOUND',
    'FORBIDDEN',
    'INVALID_OPERATION',
    'UNAUTHORIZED',
  ]),
  message: z.string(),
  details: z.object({
    errors: z.array(z.object({
      field: z.string(),
      message: z.string(),
      type: z.string(),
    })),
  }).optional(),
})

export type TaskErrorResponse = z.infer<typeof TaskErrorResponseSchema>

// ============================================================================
// Analytics Types (computed client-side)
// ============================================================================

export interface TaskAnalytics {
  statusDistribution: {
    pending: number
    'in-progress': number
    completed: number
  }
  priorityDistribution: {
    low: number
    medium: number
    high: number
  }
  completionTrend: {
    date: string  // ISO date (YYYY-MM-DD)
    completed: number
  }[]
}

/**
 * Compute analytics from task list
 */
export function computeAnalytics(tasks: Task[]): TaskAnalytics {
  const nonDeletedTasks = tasks.filter(t => t.status !== 'deleted')

  // Status distribution
  const statusDistribution = {
    pending: nonDeletedTasks.filter(t => t.status === 'pending').length,
    'in-progress': nonDeletedTasks.filter(t => t.status === 'in-progress').length,
    completed: nonDeletedTasks.filter(t => t.status === 'completed').length,
  }

  // Priority distribution
  const priorityDistribution = {
    low: nonDeletedTasks.filter(t => t.priority === 'low').length,
    medium: nonDeletedTasks.filter(t => t.priority === 'medium').length,
    high: nonDeletedTasks.filter(t => t.priority === 'high').length,
  }

  // Completion trend (last 30 days)
  const completedTasks = tasks.filter(t => t.status === 'completed')
  const last30Days = Array.from({ length: 30 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - i)
    return date.toISOString().split('T')[0]
  }).reverse()

  const completionTrend = last30Days.map(date => ({
    date,
    completed: completedTasks.filter(t =>
      t.updated_at.startsWith(date)
    ).length,
  }))

  return {
    statusDistribution,
    priorityDistribution,
    completionTrend,
  }
}
