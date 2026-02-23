"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils/cn";

interface AuthCardProps {
  children: React.ReactNode;
  className?: string;
}

export function AuthCard({ children, className }: AuthCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "w-full max-w-md mx-auto",
        "backdrop-blur-2xl bg-white/5 border border-white/10",
        "rounded-3xl shadow-[0_30px_80px_rgba(0,0,0,0.45)] p-8",
        className
      )}
    >
      {children}
    </motion.div>
  );
}
