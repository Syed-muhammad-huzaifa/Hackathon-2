/**
 * Sign-out button component
 *
 * @spec specs/003-todo-frontend/spec.md (FR-008, US2)
 */

'use client';

import { Button } from '@/components/ui/button';
import { LogOut, Loader2 } from 'lucide-react';
import { signOut } from '@/lib/api/auth';
import { toast } from 'sonner';
import { useState } from 'react';

export function SignOutButton() {
  const [isLoading, setIsLoading] = useState(false);

  const handleSignOut = async () => {
    setIsLoading(true);

    try {
      await signOut();
      toast.success('Signed out successfully');
      window.location.href = '/';
    } catch {
      toast.error('Failed to sign out');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      variant="ghost"
      className="w-full justify-start text-muted-foreground hover:text-foreground"
      onClick={handleSignOut}
      disabled={isLoading}
    >
      {isLoading ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : (
        <LogOut className="mr-2 h-4 w-4" />
      )}
      Sign Out
    </Button>
  );
}
