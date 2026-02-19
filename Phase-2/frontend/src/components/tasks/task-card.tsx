/**
 * Premium task card component with smooth interactions
 *
 * @spec specs/003-todo-frontend/spec.md (FR-012, FR-021, FR-024, US3)
 */

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import React from 'react';
import { Edit, Trash2, Clock, CheckCircle2, Circle, Check } from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils';
import type { Task, TaskStatus, TaskPriority } from '@/types/task';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  onStatusChange: (task: Task, status: TaskStatus) => void;
}

const priorityConfig: Record<TaskPriority, { color: string; gradient: string; badge: string }> = {
  low: {
    color: 'bg-blue-500',
    gradient: 'from-blue-500 to-cyan-500',
    badge: 'bg-blue-500/10 text-blue-400 border-blue-500/20 hover:bg-blue-500/20',
  },
  medium: {
    color: 'bg-yellow-500',
    gradient: 'from-yellow-500 to-orange-500',
    badge: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20 hover:bg-yellow-500/20',
  },
  high: {
    color: 'bg-red-500',
    gradient: 'from-red-500 to-pink-500',
    badge: 'bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20',
  },
};

const statusConfig: Record<TaskStatus, { badge: string; icon: React.ElementType }> = {
  pending: {
    badge: 'bg-slate-500/10 text-slate-400 border-slate-500/20 hover:bg-slate-500/20',
    icon: Circle,
  },
  'in-progress': {
    badge: 'bg-blue-500/10 text-blue-400 border-blue-500/20 hover:bg-blue-500/20',
    icon: Clock,
  },
  completed: {
    badge: 'bg-green-500/10 text-green-400 border-green-500/20 hover:bg-green-500/20',
    icon: CheckCircle2,
  },
  deleted: {
    badge: 'bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20',
    icon: Trash2,
  },
};

export function TaskCard({ task, onEdit, onDelete, onStatusChange }: TaskCardProps) {
  const StatusIcon = statusConfig[task.status].icon;

  return (
    <Card className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-6 hover:scale-[1.01] transition-all duration-300 cursor-pointer group animate-slide-up">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-4">
          {/* Header with Priority Indicator */}
          <div className="flex items-start gap-3">
            <div className={`w-1.5 h-16 rounded-full bg-gradient-to-b ${priorityConfig[task.priority].gradient} shadow-lg`} />
            <div className="flex-1 space-y-2">
              <h3 className="text-xl font-bold text-white group-hover:text-primary transition-colors duration-200">
                {task.title}
              </h3>
              {task.description && (
                <p className="text-sm text-slate-400 leading-relaxed line-clamp-2">
                  {task.description}
                </p>
              )}
            </div>
          </div>

          {/* Badges and Metadata */}
          <div className="flex items-center gap-2 flex-wrap">
            <Badge
              variant="outline"
              className={`${priorityConfig[task.priority].badge} transition-colors duration-200 cursor-pointer font-medium`}
            >
              {task.priority.toUpperCase()}
            </Badge>
            <Badge
              variant="outline"
              className={`${statusConfig[task.status].badge} transition-colors duration-200 cursor-pointer font-medium flex items-center gap-1`}
            >
              <StatusIcon className="w-3 h-3" aria-hidden="true" />
              {task.status.replace('-', ' ').toUpperCase()}
            </Badge>
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <Clock className="w-3 h-3" aria-hidden="true" />
              {formatRelativeTime(task.created_at)}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300">
          {task.status !== 'completed' && (
            <Button
              size="icon"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                onStatusChange(task, 'completed');
              }}
              className="hover:bg-green-500/10 hover:text-green-400 transition-colors duration-200 cursor-pointer"
              aria-label={`Mark as complete: ${task.title}`}
            >
              <Check className="h-4 w-4" aria-hidden="true" />
            </Button>
          )}
          <Button
            size="icon"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(task);
            }}
            className="hover:bg-primary/10 hover:text-primary transition-colors duration-200 cursor-pointer"
            aria-label={`Edit task: ${task.title}`}
          >
            <Edit className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            size="icon"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(task);
            }}
            className="hover:bg-destructive/10 hover:text-destructive transition-colors duration-200 cursor-pointer"
            aria-label={`Delete task: ${task.title}`}
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
