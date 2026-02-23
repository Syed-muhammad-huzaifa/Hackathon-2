"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils/cn";
import { navItems } from "./DashboardSidebar";

export function DashboardMobileNav() {
  const pathname = usePathname();

  return (
    <div className="lg:hidden border-b border-white/5 bg-[#0b0f14]">
      <div className="px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-white/10 border border-white/10 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-white">TaskAI</p>
            <p className="text-xs text-zinc-500">Dashboard</p>
          </div>
        </div>
        <span className="text-xs px-2 py-1 rounded-full border border-white/10 text-zinc-400">
          Secure
        </span>
      </div>
      <div className="px-4 pb-4 overflow-x-auto">
        <div className="flex gap-2 min-w-max">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "px-3 py-1.5 rounded-full text-xs font-medium border transition-colors",
                  isActive
                    ? "bg-blue-500/15 text-blue-200 border-blue-500/30"
                    : "text-zinc-400 border-white/10 hover:text-white hover:border-white/20"
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
