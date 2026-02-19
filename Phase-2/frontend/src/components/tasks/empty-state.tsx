/**
 * Premium empty state component for tasks
 *
 * @spec specs/003-todo-frontend/spec.md (FR-013, US3)
 */

import { Plus, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface EmptyStateProps {
  onCreateTask?: () => void;
}

export function EmptyState({ onCreateTask }: EmptyStateProps) {
  return (
    <div className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-16 text-center space-y-6 backdrop-blur-xl animate-fade-in">
      {/* Icon with gradient background */}
      <div className="relative mx-auto w-24 h-24">
        <div className="absolute inset-0 bg-gradient-to-br from-primary via-secondary to-accent rounded-3xl blur-xl opacity-50 animate-pulse" />
        <div className="relative w-24 h-24 rounded-3xl bg-gradient-to-br from-primary via-secondary to-accent flex items-center justify-center shadow-2xl shadow-primary/50">
          <Sparkles className="w-12 h-12 text-white" aria-hidden="true" />
        </div>
      </div>

      {/* Content */}
      <div className="space-y-3">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Ready to Get Started?
        </h2>
        <p className="text-lg text-slate-400 max-w-md mx-auto leading-relaxed">
          Create your first task and begin your journey to enhanced productivity. Every great achievement starts with a single step.
        </p>
      </div>

      {/* CTA Button */}
      {onCreateTask && (
        <Button
          onClick={onCreateTask}
          size="lg"
          className="bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-all duration-300 text-base font-semibold shadow-lg shadow-primary/30 cursor-pointer px-8 py-6"
        >
          <Plus className="mr-2 h-5 w-5" aria-hidden="true" />
          Create Your First Task
        </Button>
      )}

      {/* Decorative elements */}
      <div className="flex items-center justify-center gap-2 pt-4 text-sm text-slate-500">
        <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
        <span>Start organizing your work today</span>
        <div className="w-2 h-2 rounded-full bg-secondary animate-pulse" style={{ animationDelay: '0.5s' }} />
      </div>
    </div>
  );
}
