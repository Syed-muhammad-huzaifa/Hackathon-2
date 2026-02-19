/**
 * Sign-in page with premium glassmorphism design
 *
 * @spec specs/003-todo-frontend/spec.md (FR-004, US2)
 */

import { SignInForm } from '@/components/auth/sign-in-form';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-[#020617]">
      {/* Mesh Gradient Background */}
      <div className="absolute inset-0 [background:radial-gradient(at_0%_0%,oklch(0.628_0.194_293.498_/_0.3)_0px,transparent_50%),radial-gradient(at_100%_0%,oklch(0.588_0.233_263.711_/_0.3)_0px,transparent_50%),radial-gradient(at_100%_100%,oklch(0.724_0.149_200.801_/_0.3)_0px,transparent_50%),radial-gradient(at_0%_100%,oklch(0.628_0.194_293.498_/_0.3)_0px,transparent_50%)] animate-gradient" />

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 [background-image:linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] [background-size:50px_50px] opacity-20" />

      {/* Floating Abstract Shapes */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-20 right-10 w-80 h-80 bg-secondary/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />

      {/* Back to Home Link */}
      <Link
        href="/"
        className="absolute top-8 left-8 flex items-center gap-2 text-slate-400 hover:text-white transition-colors duration-200 cursor-pointer group"
      >
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" aria-hidden="true" />
        <span>Back to Home</span>
      </Link>

      <div className="w-full max-w-md relative z-10 space-y-8 animate-fade-in">
        {/* Header */}
        <div className="text-center space-y-3">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            Welcome Back
          </h1>
          <p className="text-lg text-slate-400">
            Sign in to continue your productivity journey
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-card/50 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl p-8 md:p-10 backdrop-blur-2xl animate-slide-up">
          <SignInForm />
        </div>

        {/* Sign Up Link */}
        <p className="text-center text-slate-400">
          Don&apos;t have an account?{' '}
          <Link
            href="/sign-up"
            className="text-primary hover:text-secondary transition-colors duration-200 font-semibold cursor-pointer"
          >
            Create one now
          </Link>
        </p>
      </div>
    </div>
  );
}
