/**
 * Premium task form component for create/edit
 *
 * @spec specs/003-todo-frontend/spec.md (FR-016, FR-017, FR-020, US3)
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { TaskCreateRequestSchema, type TaskCreateRequest, type TaskUpdateRequest } from '@/lib/schemas/task';
import { createTask, updateTask } from '@/lib/api/tasks';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, FileText, AlignLeft, Flag } from 'lucide-react';
import { toast } from 'sonner';
import type { Task } from '@/types/task';

interface TaskFormProps {
  userId: string;
  task?: Task;
  onSuccess: (task: Task) => void;
  onCancel: () => void;
}

export function TaskForm({ userId, task, onSuccess, onCancel }: TaskFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const isEditing = !!task;

  type FormData = {
    title: string;
    description?: string;
    priority?: 'low' | 'medium' | 'high';
  };

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(TaskCreateRequestSchema),
    defaultValues: task ? {
      title: task.title,
      description: task.description || undefined,
      priority: task.priority,
    } : {
      priority: 'medium',
    },
  });

  const priority = watch('priority');

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);

    try {
      if (isEditing) {
        const response = await updateTask(userId, task.id, data as TaskUpdateRequest);
        toast.success('Task updated successfully');
        onSuccess(response.data);
      } else {
        const response = await createTask(userId, data as TaskCreateRequest);
        toast.success('Task created successfully');
        onSuccess(response.data);
      }
    } catch {
      toast.error(isEditing ? 'Failed to update task' : 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Title Field */}
      <div className="space-y-2">
        <Label htmlFor="title" className="text-sm font-medium text-slate-300">
          Task Title
        </Label>
        <div className="relative group">
          <FileText
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-primary transition-colors duration-200"
            aria-hidden="true"
          />
          <Input
            id="title"
            type="text"
            placeholder="Enter a clear, actionable title…"
            autoComplete="off"
            disabled={isLoading}
            {...register('title')}
            className={`pl-11 h-12 bg-white/5 border-white/10 focus-visible:border-primary focus-visible:ring-primary/20 transition-all duration-300 ${
              errors.title ? 'border-destructive focus-visible:border-destructive focus-visible:ring-destructive/20' : ''
            }`}
          />
        </div>
        {errors.title && (
          <p className="text-sm text-destructive flex items-center gap-1 animate-slide-up">
            {errors.title.message}
          </p>
        )}
      </div>

      {/* Description Field */}
      <div className="space-y-2">
        <Label htmlFor="description" className="text-sm font-medium text-slate-300">
          Description <span className="text-slate-500">(optional)</span>
        </Label>
        <div className="relative group">
          <AlignLeft
            className="absolute left-3 top-3 w-5 h-5 text-slate-400 group-focus-within:text-primary transition-colors duration-200"
            aria-hidden="true"
          />
          <textarea
            id="description"
            placeholder="Add more details about this task…"
            disabled={isLoading}
            {...register('description')}
            className={`flex min-h-[100px] w-full rounded-xl border bg-white/5 border-white/10 px-3 py-3 pl-11 text-sm ring-offset-background placeholder:text-slate-500 focus-visible:outline-none focus-visible:border-primary focus-visible:ring-[3px] focus-visible:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-300 resize-none ${
              errors.description ? 'border-destructive focus-visible:border-destructive focus-visible:ring-destructive/20' : ''
            }`}
          />
        </div>
        {errors.description && (
          <p className="text-sm text-destructive flex items-center gap-1 animate-slide-up">
            {errors.description.message}
          </p>
        )}
      </div>

      {/* Priority Field */}
      <div className="space-y-2">
        <Label htmlFor="priority" className="text-sm font-medium text-slate-300 flex items-center gap-2">
          <Flag className="w-4 h-4" aria-hidden="true" />
          Priority Level
        </Label>
        <Select
          value={priority}
          onValueChange={(value) => setValue('priority', value as 'low' | 'medium' | 'high')}
          disabled={isLoading}
        >
          <SelectTrigger className="h-12 bg-white/5 border-white/10 focus:border-primary focus:ring-primary/20 transition-all duration-300">
            <SelectValue placeholder="Select priority level" />
          </SelectTrigger>
          <SelectContent className="bg-[#1E293B] border-white/10 backdrop-blur-xl">
            <SelectItem value="low" className="focus:bg-blue-500/10 focus:text-blue-400 cursor-pointer">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-blue-500" />
                Low Priority
              </div>
            </SelectItem>
            <SelectItem value="medium" className="focus:bg-yellow-500/10 focus:text-yellow-400 cursor-pointer">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-yellow-500" />
                Medium Priority
              </div>
            </SelectItem>
            <SelectItem value="high" className="focus:bg-red-500/10 focus:text-red-400 cursor-pointer">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-red-500" />
                High Priority
              </div>
            </SelectItem>
          </SelectContent>
        </Select>
        {errors.priority && (
          <p className="text-sm text-destructive flex items-center gap-1 animate-slide-up">
            {errors.priority.message}
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3 pt-4">
        <Button
          type="submit"
          className="flex-1 h-12 bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-all duration-300 shadow-lg shadow-primary/30 cursor-pointer font-semibold"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" aria-hidden="true" />
              {isEditing ? 'Updating…' : 'Creating…'}
            </>
          ) : (
            isEditing ? 'Update Task' : 'Create Task'
          )}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
          className="h-12 border-white/10 hover:bg-white/5 transition-colors duration-300 cursor-pointer"
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
