/**
 * Premium footer component
 *
 * @spec specs/003-todo-frontend/spec.md (FR-001, US1)
 */

import Link from 'next/link';
import { Sparkles, Github, Twitter, Linkedin } from 'lucide-react';

export function Footer() {
  return (
    <footer className="relative border-t border-white/10 py-16 mt-auto overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-t from-primary/5 to-transparent" />

      <div className="container mx-auto px-4 relative z-10">
        <div className="grid md:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <div className="space-y-4">
            <Link href="/" className="flex items-center gap-3 group cursor-pointer">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-primary to-secondary rounded-xl blur-md opacity-50 group-hover:opacity-75 transition-opacity" />
                <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg">
                  <Sparkles className="w-5 h-5 text-white" aria-hidden="true" />
                </div>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                TaskFlow
              </span>
            </Link>
            <p className="text-sm text-slate-400 leading-relaxed">
              Premium task management for modern professionals. Elevate your productivity.
            </p>
          </div>

          {/* Product */}
          <div className="space-y-4">
            <h3 className="font-semibold text-white">Product</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Integrations
                </Link>
              </li>
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Changelog
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div className="space-y-4">
            <h3 className="font-semibold text-white">Company</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  About
                </Link>
              </li>
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Careers
                </Link>
              </li>
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div className="space-y-4">
            <h3 className="font-semibold text-white">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Cookie Policy
                </Link>
              </li>
              <li>
                <Link href="#" className="text-slate-400 hover:text-primary transition-colors duration-200 cursor-pointer">
                  Security
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-sm text-slate-400">
            © 2026 TaskFlow. All rights reserved.
          </div>

          {/* Social links */}
          <div className="flex items-center gap-4">
            <a
              href="#"
              className="w-10 h-10 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center transition-colors duration-200 cursor-pointer group"
              aria-label="Follow us on Twitter"
            >
              <Twitter className="w-5 h-5 text-slate-400 group-hover:text-primary transition-colors" aria-hidden="true" />
            </a>
            <a
              href="#"
              className="w-10 h-10 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center transition-colors duration-200 cursor-pointer group"
              aria-label="Follow us on GitHub"
            >
              <Github className="w-5 h-5 text-slate-400 group-hover:text-primary transition-colors" aria-hidden="true" />
            </a>
            <a
              href="#"
              className="w-10 h-10 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center transition-colors duration-200 cursor-pointer group"
              aria-label="Follow us on LinkedIn"
            >
              <Linkedin className="w-5 h-5 text-slate-400 group-hover:text-primary transition-colors" aria-hidden="true" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
