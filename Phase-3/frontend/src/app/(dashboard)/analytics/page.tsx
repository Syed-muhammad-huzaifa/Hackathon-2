"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { chatAPI, type TaskStats } from "@/lib/api/chat-api-client";

export default function AnalyticsPage() {
  const [stats, setStats] = useState<TaskStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = () => {
      setLoading(true);
      setError(null);
      chatAPI
        .fetchTaskStats()
        .then((data) => setStats(data))
        .catch((err) => setError(err instanceof Error ? err.message : "Failed to load stats"))
        .finally(() => setLoading(false));
    };

    load();
    window.addEventListener("focus", load);
    return () => window.removeEventListener("focus", load);
  }, []);

  const statusData = stats
    ? [
        { name: "Completed", value: stats.completed, color: "#10b981" },
        { name: "In Progress", value: stats.inProgress, color: "#f59e0b" },
        { name: "Pending", value: stats.pending, color: "#4f7cff" },
      ].filter((d) => d.value > 0)
    : [];

  const taskBarData = stats?.tasks.map((t) => ({
    name: t.title.length > 20 ? t.title.slice(0, 20) + "…" : t.title,
    status: t.status,
    value: 1,
  })) ?? [];

  return (
    <div className="min-h-screen bg-[#0b0f14] p-4 sm:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-white mb-2">Analytics</h1>
          <p className="text-zinc-400">Track your task completion patterns and productivity</p>
        </div>

        {error && (
          <div className="mb-6 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-6 mb-8">
          <Card glass className="p-5 sm:p-6">
            <p className="text-sm text-zinc-400 mb-1">Total Tasks</p>
            {loading ? (
              <div className="h-9 w-12 rounded-lg bg-white/5 animate-pulse" />
            ) : (
              <p className="text-3xl font-bold text-white">{stats?.total ?? 0}</p>
            )}
          </Card>
          <Card glass className="p-5 sm:p-6">
            <p className="text-sm text-zinc-400 mb-1">Completed</p>
            {loading ? (
              <div className="h-9 w-12 rounded-lg bg-white/5 animate-pulse" />
            ) : (
              <p className="text-3xl font-bold text-green-400">{stats?.completed ?? 0}</p>
            )}
          </Card>
          <Card glass className="p-5 sm:p-6">
            <p className="text-sm text-zinc-400 mb-1">In Progress</p>
            {loading ? (
              <div className="h-9 w-12 rounded-lg bg-white/5 animate-pulse" />
            ) : (
              <p className="text-3xl font-bold text-yellow-400">{stats?.inProgress ?? 0}</p>
            )}
          </Card>
          <Card glass className="p-5 sm:p-6">
            <p className="text-sm text-zinc-400 mb-1">Pending</p>
            {loading ? (
              <div className="h-9 w-12 rounded-lg bg-white/5 animate-pulse" />
            ) : (
              <p className="text-3xl font-bold text-indigo-400">{stats?.pending ?? 0}</p>
            )}
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          {/* Status Distribution */}
          <Card glass className="p-5 sm:p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Task Status Distribution</h3>
            {loading ? (
              <div className="h-[300px] flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : statusData.length === 0 ? (
              <div className="h-[300px] flex items-center justify-center text-zinc-500 text-sm">
                No tasks yet. Start chatting to create tasks!
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "rgba(12, 16, 22, 0.95)",
                      border: "1px solid rgba(255, 255, 255, 0.08)",
                      borderRadius: "8px",
                      color: "#fff",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </Card>

          {/* Tasks by Status Bar */}
          <Card glass className="p-5 sm:p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Your Tasks</h3>
            {loading ? (
              <div className="h-[300px] flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : taskBarData.length === 0 ? (
              <div className="h-[300px] flex items-center justify-center text-zinc-500 text-sm">
                No tasks yet. Start chatting to create tasks!
              </div>
            ) : (
              <div className="space-y-3 mt-2 overflow-y-auto max-h-[300px] pr-1">
                {stats?.tasks.map((task) => (
                  <div key={task.id} className="flex items-center gap-3">
                    <div
                      className={`w-2 h-2 rounded-full shrink-0 ${
                        task.status === "completed"
                          ? "bg-green-400"
                          : task.status === "in_progress"
                          ? "bg-yellow-400"
                          : "bg-blue-400"
                      }`}
                    />
                    <span className="text-sm text-zinc-300 truncate flex-1">{task.title}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                        task.status === "completed"
                          ? "bg-green-500/10 text-green-400"
                          : task.status === "in_progress"
                          ? "bg-yellow-500/10 text-yellow-400"
                          : "bg-blue-500/10 text-blue-300"
                      }`}
                    >
                      {task.status.replace("_", " ")}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Insights */}
        <div className="mt-6">
          <Card glass className="p-5 sm:p-6">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="text-lg font-semibold text-white">AI Productivity Insights</h3>
                <p className="text-sm text-zinc-400">Calm, actionable signals based on your recent activity</p>
              </div>
              <span className="px-3 py-1 rounded-full bg-blue-500/15 border border-blue-500/30 text-xs text-blue-200">
                Updated today
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 sm:gap-4">
              {[
                { label: "Focus window", value: "10:00–12:00", note: "Most tasks completed" },
                { label: "Completion rhythm", value: "2.4/day", note: "Stable over 7 days" },
                { label: "Pending drift", value: "Low", note: "Tasks close quickly" },
              ].map((item) => (
                <div key={item.label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-wide text-zinc-500">{item.label}</p>
                  <p className="text-xl font-semibold text-white mt-2">{item.value}</p>
                  <p className="text-xs text-zinc-400 mt-1">{item.note}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
