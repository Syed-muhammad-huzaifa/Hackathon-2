/**
 * Premium header with mobile menu
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Sparkles, Menu, X } from 'lucide-react';

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <>
      {/* Desktop & Mobile Header */}
      <header className="fixed top-0 left-0 right-0 z-50 animate-fade-in">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mt-4 bg-[#0b0d1e]/95 backdrop-blur-2xl border border-white/[0.12] rounded-2xl px-4 sm:px-6 py-3.5 flex items-center justify-between shadow-2xl shadow-black/20">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2.5 group cursor-pointer z-10">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-primary to-secondary rounded-xl blur-lg opacity-60 group-hover:opacity-90 transition-opacity" />
                <div className="relative w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg">
                  <Sparkles className="w-4.5 h-4.5 text-white" aria-hidden="true" />
                </div>
              </div>
              <span className="text-xl sm:text-2xl font-black bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
                TaskFlow
              </span>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center gap-2">
              <Button
                variant="ghost"
                asChild
                className="text-slate-300 hover:text-white hover:bg-white/[0.08] transition-all duration-200 cursor-pointer font-medium"
              >
                <Link href="/sign-in">Sign In</Link>
              </Button>
              <Button
                asChild
                className="bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-all duration-300 shadow-lg shadow-primary/30 cursor-pointer font-semibold"
              >
                <Link href="/sign-up">Get Started</Link>
              </Button>
            </nav>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-white/[0.08] transition-colors text-white"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden animate-fade-in"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="fixed top-20 left-4 right-4 z-50 md:hidden animate-slide-up">
            <div className="bg-[#0b0d1e]/98 backdrop-blur-2xl border border-white/[0.12] rounded-2xl p-6 shadow-2xl">
              <nav className="flex flex-col gap-3">
                <Button
                  variant="ghost"
                  asChild
                  className="w-full justify-start text-slate-300 hover:text-white hover:bg-white/[0.08] transition-all duration-200 cursor-pointer font-medium text-base h-12"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Link href="/sign-in">Sign In</Link>
                </Button>
                <Button
                  asChild
                  className="w-full bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-all duration-300 shadow-lg shadow-primary/30 cursor-pointer font-semibold text-base h-12"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Link href="/sign-up">Get Started Free</Link>
                </Button>
              </nav>
            </div>
          </div>
        </>
      )}
    </>
  );
}
