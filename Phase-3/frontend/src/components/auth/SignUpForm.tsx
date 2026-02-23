"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { signUp } from "@/lib/auth/auth-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function SignUpForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", email: "", password: "", confirmPassword: "" });
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate() {
    const errors: Record<string, string> = {};
    if (!form.name.trim()) errors["name"] = "Name is required";
    if (!form.email.includes("@")) errors["email"] = "Enter a valid email";
    if (form.password.length < 8) errors["password"] = "Password must be at least 8 characters";
    if (form.password !== form.confirmPassword) errors["confirmPassword"] = "Passwords do not match";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setIsLoading(true);
    setError(null);

    const { error: authError } = await signUp.email({
      name: form.name,
      email: form.email,
      password: form.password,
    });

    if (authError) {
      setError(authError.message ?? "Failed to create account. Please try again.");
      setIsLoading(false);
      return;
    }

    router.push("/chatbot");
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-white/8 border border-white/10 mb-4 shadow-[0_12px_30px_rgba(79,124,255,0.25)]">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-white">Create account</h1>
        <p className="text-zinc-400 text-sm mt-1">Start managing tasks with AI</p>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
        >
          {error}
        </motion.div>
      )}

      <Input
        label="Full name"
        type="text"
        placeholder="John Doe"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        error={fieldErrors["name"]}
        autoComplete="name"
        required
      />

      <Input
        label="Email address"
        type="email"
        placeholder="you@example.com"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
        error={fieldErrors["email"]}
        autoComplete="email"
        required
      />

      <Input
        label="Password"
        type="password"
        placeholder="Min. 8 characters"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
        error={fieldErrors["password"]}
        autoComplete="new-password"
        required
      />

      <Input
        label="Confirm password"
        type="password"
        placeholder="Repeat your password"
        value={form.confirmPassword}
        onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
        error={fieldErrors["confirmPassword"]}
        autoComplete="new-password"
        required
      />

      <Button type="submit" isLoading={isLoading} className="w-full mt-2">
        {isLoading ? "Creating account..." : "Create account"}
      </Button>

      <p className="text-center text-sm text-zinc-400 mt-4">
        Already have an account?{" "}
        <Link href="/signin" className="text-blue-300 hover:text-blue-200 font-medium">
          Sign in
        </Link>
      </p>
    </form>
  );
}
