/**
 * Task list component with optimistic updates
 *
 * @spec specs/003-todo-frontend/spec.md (FR-011, FR-014, FR-022, US3)
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { TaskCard } from './task-card';
import { EmptyState } from './empty-state';
import { TaskForm } from './task-form';
import { TaskDeleteDialog } from './task-delete-dialog';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Plus, Loader2 } from 'lucide-react';
import { fetchTasks, updateTask, deleteTask } from '@/lib/api/tasks';
import { revalidateDashboard } from '@/app/actions';
import { toast } from 'sonner';
import type { Task, TaskStatus } from '@/types/task';

interface TaskListProps {
  initialTasks: Task[];
  userId: string;
}

export function TaskList({ initialTasks, userId }: TaskListProps) {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  // Re-fetch tasks client-side on mount to ensure fresh data.
  // This handles: client-side navigation, server-side fetch failures,
  // and page refreshes where the server auth might have been stale.
  useEffect(() => {
    let cancelled = false;

    async function loadTasks() {
      setIsLoading(true);
      try {
        const response = await fetchTasks(userId);
        if (!cancelled) {
          setTasks(response.data);
        }
      } catch {
        // Silently keep initialTasks — server already provided them (or empty)
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    loadTasks();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  const handleEdit = (task: Task) => {
    setSelectedTask(task);
    setIsEditDialogOpen(true);
  };

  const handleDelete = (task: Task) => {
    setSelectedTask(task);
    setIsDeleteDialogOpen(true);
  };

  const handleStatusChange = async (task: Task, status: TaskStatus) => {
    // Optimistic update
    const previousTasks = tasks;
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? { ...t, status } : t))
    );

    try {
      await updateTask(userId, task.id, { status });
      toast.success('Task status updated');
      // Invalidate all dashboard routes so overview/analytics show fresh data
      await revalidateDashboard();
      router.refresh();
    } catch {
      // Rollback on error
      setTasks(previousTasks);
      toast.error('Failed to update task status');
    }
  };

  const handleTaskCreated = async (newTask: Task) => {
    setTasks((prev) => [newTask, ...prev]);
    setIsCreateDialogOpen(false);
    // Invalidate all dashboard routes so overview/analytics show fresh data
    await revalidateDashboard();
    router.refresh();
  };

  const handleTaskUpdated = async (updatedTask: Task) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
    setIsEditDialogOpen(false);
    setSelectedTask(null);
    // Invalidate all dashboard routes so overview/analytics show fresh data
    await revalidateDashboard();
    router.refresh();
  };

  const handleTaskDeleted = async () => {
    if (!selectedTask) return;

    const taskToDelete = selectedTask;
    const previousTasks = tasks;

    // Optimistic update
    setTasks((prev) => prev.filter((t) => t.id !== taskToDelete.id));
    setIsDeleteDialogOpen(false);
    setSelectedTask(null);

    try {
      await deleteTask(userId, taskToDelete.id);
      toast.success('Task deleted successfully');
      // Invalidate all dashboard routes so overview/analytics show fresh data
      await revalidateDashboard();
      router.refresh();
    } catch {
      // Rollback on error
      setTasks(previousTasks);
      toast.error('Failed to delete task');
    }
  };

  if (isLoading && tasks.length === 0) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!isLoading && tasks.length === 0) {
    return (
      <>
        <EmptyState onCreateTask={() => setIsCreateDialogOpen(true)} />

        {/* Create Task Dialog (from EmptyState button) */}
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogContent className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl backdrop-blur-2xl border-white/10">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold">Create New Task</DialogTitle>
            </DialogHeader>
            <TaskForm
              userId={userId}
              onSuccess={handleTaskCreated}
              onCancel={() => setIsCreateDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-1 h-8 bg-gradient-to-b from-primary to-secondary rounded-full" />
            Your Tasks
          </h2>
          <p className="text-slate-400 mt-2 ml-4">
            {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'} in total
          </p>
        </div>
        <Button
          onClick={() => setIsCreateDialogOpen(true)}
          className="bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-all duration-300 shadow-lg shadow-primary/30 cursor-pointer"
        >
          <Plus className="mr-2 h-4 w-4" aria-hidden="true" />
          Add Task
        </Button>
      </div>

      <div className="grid gap-4">
        {tasks.map((task, index) => (
          <div
            key={task.id}
            style={{ animationDelay: `${index * 50}ms` }}
            className="animate-slide-up"
          >
            <TaskCard
              task={task}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onStatusChange={handleStatusChange}
            />
          </div>
        ))}
      </div>

      {/* Create Task Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl backdrop-blur-2xl border-white/10">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">Create New Task</DialogTitle>
          </DialogHeader>
          <TaskForm
            userId={userId}
            onSuccess={handleTaskCreated}
            onCancel={() => setIsCreateDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Edit Task Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl backdrop-blur-2xl border-white/10">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">Edit Task</DialogTitle>
          </DialogHeader>
          {selectedTask && (
            <TaskForm
              userId={userId}
              task={selectedTask}
              onSuccess={handleTaskUpdated}
              onCancel={() => {
                setIsEditDialogOpen(false);
                setSelectedTask(null);
              }}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <TaskDeleteDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        onConfirm={handleTaskDeleted}
        taskTitle={selectedTask?.title || ''}
      />
    </div>
  );
}
