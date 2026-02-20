/**
 * Sign-in form component with premium floating labels
 *
 * @spec specs/003-todo-frontend/spec.md (FR-004, FR-005, FR-006, US2)
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { SignInRequestSchema, type SignInRequest } from '@/lib/schemas/auth';
import { signIn } from '@/lib/api/auth';
import { isAPIError, getErrorMessage } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, Mail, Lock } from 'lucide-react';
import { toast } from 'sonner';

export function SignInForm() {
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignInRequest>({
    resolver: zodResolver(SignInRequestSchema),
  });

  const onSubmit = async (data: SignInRequest) => {
    setIsLoading(true);

    try {
      await signIn(data);

      toast.success('Welcome back!');

      // Wait a bit for session cookie to be set, then redirect
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 500);
    } catch (error) {
      if (isAPIError(error)) {
        if (error.code === 'INVALID_CREDENTIALS') {
          toast.error('Invalid email or password');
        } else if (error.code === 'VALIDATION_ERROR') {
          toast.error('Please check your input and try again');
        } else {
          toast.error(error.message || 'Failed to sign in');
        }
      } else {
        toast.error(getErrorMessage(error));
      }
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Email Field */}
      <div className="space-y-2">
        <Label htmlFor="email" className="text-sm font-medium text-slate-300">
          Email Address
        </Label>
        <div className="relative group">
          <Mail
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-primary transition-colors duration-200"
            aria-hidden="true"
          />
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            disabled={isLoading}
            {...register('email')}
            className={`pl-11 h-12 bg-white/5 border-white/10 focus-visible:border-primary focus-visible:ring-primary/20 transition-all duration-300 ${
              errors.email ? 'border-destructive focus-visible:border-destructive focus-visible:ring-destructive/20' : ''
            }`}
          />
        </div>
        {errors.email && (
          <p className="text-sm text-destructive flex items-center gap-1 animate-slide-up">
            {errors.email.message}
          </p>
        )}
      </div>

      {/* Password Field */}
      <div className="space-y-2">
        <Label htmlFor="password" className="text-sm font-medium text-slate-300">
          Password
        </Label>
        <div className="relative group">
          <Lock
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-primary transition-colors duration-200"
            aria-hidden="true"
          />
          <Input
            id="password"
            type="password"
            placeholder="Enter your password"
            autoComplete="current-password"
            disabled={isLoading}
            {...register('password')}
            className={`pl-11 h-12 bg-white/5 border-white/10 focus-visible:border-primary focus-visible:ring-primary/20 transition-all duration-300 ${
              errors.password ? 'border-destructive focus-visible:border-destructive focus-visible:ring-destructive/20' : ''
            }`}
          />
        </div>
        {errors.password && (
          <p className="text-sm text-destructive flex items-center gap-1 animate-slide-up">
            {errors.password.message}
          </p>
        )}
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        className="w-full h-12 bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-all duration-300 text-base font-semibold shadow-lg shadow-primary/30 cursor-pointer"
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" aria-hidden="true" />
            Signing in…
          </>
        ) : (
          'Sign In'
        )}
      </Button>
    </form>
  );
}
