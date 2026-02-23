import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0b0f14] text-white overflow-hidden">
      {/* Ambient background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute -top-24 -left-16 h-80 w-80 rounded-full bg-blue-500/10 blur-[120px]" />
        <div className="absolute top-32 right-10 h-72 w-72 rounded-full bg-blue-400/10 blur-[120px]" />
        <div className="absolute bottom-0 left-1/3 h-96 w-96 rounded-full bg-white/5 blur-[160px]" />
      </div>

      {/* Nav */}
      <nav className="relative flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-white/10 border border-white/10 flex items-center justify-center shadow-[0_10px_25px_rgba(79,124,255,0.2)]">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span className="text-lg font-semibold text-white tracking-tight">TaskAI</span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/signin"
            className="px-4 py-2 text-sm font-medium text-zinc-300 hover:text-white transition-colors"
          >
            Sign in
          </Link>
          <Link
            href="/signup"
            className="px-5 py-2 rounded-xl text-sm font-semibold bg-primary text-white shadow-[0_12px_30px_rgba(79,124,255,0.25)] hover:brightness-110 transition-all duration-200"
          >
            Start free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative text-center px-6 pt-20 pb-24 max-w-5xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-blue-200 text-xs font-medium mb-8">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-300 animate-pulse" />
          AI-native task control
        </div>

        <h1 className="text-5xl md:text-7xl font-semibold leading-tight tracking-tight mb-6">
          Manage tasks with{" "}
          <span className="gradient-text">conversation</span>
        </h1>

        <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          A calm, intelligent workspace where you add, update, and complete tasks using natural language. No forms, no friction.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/signup"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl text-base font-semibold bg-primary text-white shadow-[0_16px_40px_rgba(79,124,255,0.25)] hover:brightness-110 active:brightness-95 transition-all duration-200"
          >
            Start free
          </Link>
          <Link
            href="/signin"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl text-base font-semibold backdrop-blur-xl bg-white/5 border border-white/10 text-white hover:bg-white/10 hover:border-white/20 transition-all duration-200"
          >
            See demo
          </Link>
        </div>

        {/* Chat preview */}
        <div className="mt-16 max-w-2xl mx-auto">
          <div className="glass rounded-2xl p-6 text-left">
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-white/5">
              <span className="text-xs text-zinc-500">TaskAI Chat</span>
              <span className="ml-auto text-xs text-zinc-500">Live</span>
            </div>
            <div className="space-y-4">
              <div className="flex justify-end">
                <div className="max-w-[80%] px-4 py-2.5 rounded-2xl rounded-tr-sm bg-blue-500/20 border border-blue-500/30 text-white text-sm shadow-[0_12px_30px_rgba(79,124,255,0.2)]">
                  Add a task: prepare the Q4 presentation
                </div>
              </div>
              <div className="flex justify-start">
                <div className="max-w-[80%] px-4 py-2.5 rounded-2xl rounded-tl-sm backdrop-blur-xl bg-white/5 border border-white/10 text-white text-sm">
                  Done. I&apos;ve added “Prepare the Q4 presentation.”
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative px-6 py-16 max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-semibold">Everything you need</h2>
          <p className="text-zinc-400 mt-2 max-w-xl mx-auto">
            A premium, minimal workspace for task management powered by AI.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              title: "Natural Language",
              desc: "Add, update, and complete tasks with a single sentence.",
            },
            {
              title: "AI Orchestration",
              desc: "Intelligent task handling with MCP-powered actions.",
            },
            {
              title: "Calm Focus",
              desc: "Minimal UI with clean spacing and frictionless flows.",
            },
            {
              title: "Secure Auth",
              desc: "JWT + Better Auth with verified sessions and safety.",
            },
            {
              title: "Persistent Memory",
              desc: "Conversations and task history remain available anytime.",
            },
            {
              title: "Insightful Analytics",
              desc: "Understand your productivity with beautiful summaries.",
            },
          ].map((f) => (
            <div key={f.title} className="glass-hover rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="relative px-6 pb-24">
        <div className="max-w-3xl mx-auto text-center">
          <div className="glass rounded-3xl p-10 border border-blue-500/20">
            <h2 className="text-3xl font-semibold mb-3">Start your calm workflow</h2>
            <p className="text-zinc-400 mb-8">
              Create your account and manage tasks through conversation in seconds.
            </p>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl text-base font-semibold bg-primary text-white shadow-[0_16px_40px_rgba(79,124,255,0.25)] hover:brightness-110 transition-all duration-200"
            >
              Start free
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-white/5 px-6 py-8 text-center text-zinc-500 text-sm">
        <p>© 2026 TaskAI. Built for calm, intelligent productivity.</p>
      </footer>
    </div>
  );
}
