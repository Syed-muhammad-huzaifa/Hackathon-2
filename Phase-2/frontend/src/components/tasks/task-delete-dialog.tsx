/**
 * Premium task delete confirmation dialog
 *
 * @spec specs/003-todo-frontend/spec.md (FR-025, FR-026, US3)
 */

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';

interface TaskDeleteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  taskTitle: string;
}

export function TaskDeleteDialog({
  open,
  onOpenChange,
  onConfirm,
  taskTitle,
}: TaskDeleteDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl backdrop-blur-2xl border-white/10">
        <DialogHeader>
          <div className="flex items-center gap-4 mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-destructive/30 rounded-2xl blur-xl animate-pulse" />
              <div className="relative w-14 h-14 rounded-2xl bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center shadow-lg shadow-red-500/30">
                <AlertTriangle className="w-7 h-7 text-white" aria-hidden="true" />
              </div>
            </div>
            <div>
              <DialogTitle className="text-2xl font-bold">Delete Task?</DialogTitle>
              <p className="text-sm text-slate-400 mt-1">This action cannot be undone</p>
            </div>
          </div>
          <DialogDescription className="pt-4 text-base leading-relaxed">
            Are you sure you want to permanently delete{' '}
            <span className="font-semibold text-white bg-white/5 px-2 py-0.5 rounded">
              &quot;{taskTitle}&quot;
            </span>
            ? All associated data will be lost forever.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-3 sm:gap-3 pt-6">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="flex-1 h-11 border-white/10 hover:bg-white/5 transition-colors duration-300 cursor-pointer"
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={() => {
              onConfirm();
              onOpenChange(false);
            }}
            className="flex-1 h-11 bg-gradient-to-r from-red-500 to-pink-500 hover:opacity-90 transition-all duration-300 shadow-lg shadow-red-500/30 cursor-pointer font-semibold"
          >
            Delete Forever
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
