"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { chatAPI, type TaskItem } from "@/lib/api/chat-api-client";

export default function HistoryPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = () => {
      setLoading(true);
      setError(null);
      chatAPI
        .fetchCompletedTasks()
        .then((data) => setTasks(data))
        .catch((err) => setError(err instanceof Error ? err.message : "Failed to load history"))
        .finally(() => setLoading(false));
    };

    load();
    window.addEventListener("focus", load);
    return () => window.removeEventListener("focus", load);
  }, []);

  return (
    <div className="min-h-screen bg-[#0b0f14] p-4 sm:p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-white mb-2">Task History</h1>
          <p className="text-zinc-400">View your completed tasks</p>
        </div>

        {error && (
          <div className="mb-6 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error}
          </div>
        )}

        {loading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <Card key={i} glass className="p-4 sm:p-5">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-white/5 animate-pulse shrink-0" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-3/4 bg-white/5 rounded animate-pulse" />
                    <div className="h-3 w-1/2 bg-white/5 rounded animate-pulse" />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : tasks.length === 0 ? (
          <Card glass className="p-6 sm:p-8">
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">No completed tasks yet</h3>
              <p className="text-zinc-400 text-sm">
                Chat with the AI to create and complete tasks. They&apos;ll appear here once done.
              </p>
            </div>
          </Card>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <Card key={task.id} glass className="p-4 sm:p-5 hover:bg-white/10 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 bg-green-500/10 text-green-400">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-white font-medium mb-1">{task.title}</h3>
                    <div className="flex items-center gap-2 text-sm text-zinc-400">
                      <span className="px-2 py-0.5 rounded-md bg-green-500/10 text-green-400 text-xs">
                        completed
                      </span>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
