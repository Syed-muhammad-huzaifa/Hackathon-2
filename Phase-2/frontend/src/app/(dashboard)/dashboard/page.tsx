/**
 * Dashboard Overview Page
 * Shows stats summary, recent tasks, and progress breakdown
 */

import { auth } from '@/lib/auth/server';
import { computeAnalytics } from '@/lib/schemas/task';
import { redirect } from 'next/navigation';
import { headers } from 'next/headers';
import Link from 'next/link';
import type { Task } from '@/types/task';

export const dynamic = 'force-dynamic';
export const revalidate = 0;
import {
  CheckCircle2,
  Clock,
  TrendingUp,
  ListTodo,
  ArrowRight,
  Flag,
  Circle,
  BarChart3,
  CheckSquare,
} from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils';

async function getPageData() {
  const headersList = await headers();
  const session = await auth.api.getSession({ headers: headersList });
  if (!session?.user) redirect('/sign-in');

  const tokenResponse = await auth.api.getToken({ headers: headersList });
  let tasks: Task[] = [];
  if (tokenResponse?.token) {
    try {
      // Use NEXT_PUBLIC_API_URL which is available in both client and server
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://huz111-backend-todo.hf.space';
      // Add timestamp to bust Next.js cache
      const cacheBuster = `?_t=${Date.now()}`;
      const res = await fetch(`${apiUrl}/api/${session.user.id}/tasks${cacheBuster}`, {
        headers: {
          Authorization: `Bearer ${tokenResponse.token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
        next: { revalidate: 0 },
      });
      if (res.ok) {
        const data = await res.json();
        tasks = data.data || [];
      }
    } catch {
      tasks = [];
    }
  }
  return { user: session.user, tasks };
}

const priorityBadge: Record<string, string> = {
  low: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  medium: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  high: 'text-red-400 bg-red-500/10 border-red-500/20',
};

const statusConfig: Record<string, { icon: React.ElementType; color: string }> = {
  pending: { icon: Circle, color: 'text-slate-400' },
  'in-progress': { icon: Clock, color: 'text-blue-400' },
  completed: { icon: CheckCircle2, color: 'text-emerald-400' },
  deleted: { icon: Circle, color: 'text-red-400' },
};

export default async function OverviewPage() {
  const { user, tasks } = await getPageData();
  const analytics = computeAnalytics(tasks);
  const nonDeleted = tasks.filter((t) => t.status !== 'deleted');

  const completionRate =
    nonDeleted.length > 0
      ? Math.round((analytics.statusDistribution.completed / nonDeleted.length) * 100)
      : 0;

  const highPriority = nonDeleted.filter(
    (t) => t.priority === 'high' && t.status !== 'completed'
  ).length;

  const recentTasks = [...nonDeleted]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 6);

  const stats = [
    {
      label: 'Total Tasks',
      value: nonDeleted.length,
      gradient: 'from-violet-500 to-purple-600',
      shadow: 'shadow-purple-500/20',
      textColor: 'text-white',
      icon: ListTodo,
    },
    {
      label: 'Completed',
      value: analytics.statusDistribution.completed,
      gradient: 'from-emerald-500 to-green-600',
      shadow: 'shadow-emerald-500/20',
      textColor: 'text-emerald-400',
      icon: CheckCircle2,
    },
    {
      label: 'In Progress',
      value: analytics.statusDistribution['in-progress'],
      gradient: 'from-blue-500 to-cyan-600',
      shadow: 'shadow-blue-500/20',
      textColor: 'text-blue-400',
      icon: Clock,
    },
    {
      label: 'Completion Rate',
      value: `${completionRate}%`,
      gradient: 'from-pink-500 to-rose-600',
      shadow: 'shadow-pink-500/20',
      textColor: 'text-pink-400',
      icon: TrendingUp,
    },
    {
      label: 'Pending',
      value: analytics.statusDistribution.pending,
      gradient: 'from-slate-500 to-slate-600',
      shadow: 'shadow-slate-500/20',
      textColor: 'text-slate-300',
      icon: Circle,
    },
    {
      label: 'High Priority',
      value: highPriority,
      gradient: 'from-red-500 to-orange-600',
      shadow: 'shadow-red-500/20',
      textColor: 'text-red-400',
      icon: Flag,
    },
  ];

  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome header */}
      <div className="pt-2">
        <h1 className="text-3xl sm:text-4xl font-bold text-white">
          {greeting},{' '}
          <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            {user.name?.split(' ')[0] || 'there'}
          </span>{' '}
          👋
        </h1>
        <p className="text-slate-400 mt-1.5 text-base">
          Here&apos;s an overview of your tasks and productivity.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
        {stats.map(({ label, value, gradient, shadow, textColor, icon: Icon }) => (
          <div
            key={label}
            className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-4 hover:border-white/15 hover:-translate-y-0.5 transition-all duration-300 group"
          >
            <div
              className={`w-9 h-9 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg ${shadow} mb-3 group-hover:scale-110 transition-transform duration-300`}
            >
              <Icon className="w-4 h-4 text-white" aria-hidden="true" />
            </div>
            <p className={`text-2xl font-bold ${textColor}`}>{value}</p>
            <p className="text-xs text-slate-500 mt-0.5 leading-tight">{label}</p>
          </div>
        ))}
      </div>

      {/* Main content grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Tasks */}
        <div className="lg:col-span-2 bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-5 sm:p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-base font-semibold text-white">Recent Tasks</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Your latest {recentTasks.length} tasks
              </p>
            </div>
            <Link
              href="/dashboard/tasks"
              className="flex items-center gap-1.5 text-xs text-primary hover:text-primary/80 font-medium transition-colors group"
            >
              View all
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>

          {recentTasks.length === 0 ? (
            <div className="text-center py-12">
              <ListTodo className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-500 text-sm">No tasks yet.</p>
              <Link
                href="/dashboard/tasks"
                className="text-primary text-sm hover:underline mt-1.5 inline-block"
              >
                Create your first task →
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {recentTasks.map((task) => {
                const { icon: StatusIcon, color } = statusConfig[task.status] ?? statusConfig.pending;
                return (
                  <div
                    key={task.id}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/[0.025] border border-white/[0.05] hover:border-white/10 hover:bg-white/[0.05] transition-all duration-200"
                  >
                    <StatusIcon className={`w-4 h-4 flex-shrink-0 ${color}`} aria-hidden="true" />
                    <div className="flex-1 min-w-0">
                      <p
                        className={`text-sm font-medium truncate ${
                          task.status === 'completed'
                            ? 'text-slate-500 line-through'
                            : 'text-white'
                        }`}
                      >
                        {task.title}
                      </p>
                      <p className="text-xs text-slate-600 mt-0.5">
                        {formatRelativeTime(task.created_at)}
                      </p>
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${priorityBadge[task.priority]} flex-shrink-0`}
                    >
                      {task.priority.toUpperCase()}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right panel */}
        <div className="space-y-4">
          {/* Progress bars */}
          <div className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Progress</h3>
            <div className="space-y-3.5">
              {[
                {
                  label: 'Completed',
                  value: analytics.statusDistribution.completed,
                  total: nonDeleted.length,
                  bar: 'bg-emerald-500',
                  text: 'text-emerald-400',
                },
                {
                  label: 'In Progress',
                  value: analytics.statusDistribution['in-progress'],
                  total: nonDeleted.length,
                  bar: 'bg-blue-500',
                  text: 'text-blue-400',
                },
                {
                  label: 'Pending',
                  value: analytics.statusDistribution.pending,
                  total: nonDeleted.length,
                  bar: 'bg-slate-500',
                  text: 'text-slate-400',
                },
              ].map(({ label, value, total, bar, text }) => {
                const pct = total > 0 ? Math.round((value / total) * 100) : 0;
                return (
                  <div key={label}>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-slate-400">{label}</span>
                      <span className={`font-semibold ${text}`}>
                        {value}{' '}
                        <span className="text-slate-600 font-normal">({pct}%)</span>
                      </span>
                    </div>
                    <div className="h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                      <div
                        className={`h-full ${bar} rounded-full transition-all duration-700`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Priority breakdown */}
          <div className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Priority</h3>
            <div className="space-y-3">
              {[
                {
                  label: 'High',
                  value: analytics.priorityDistribution.high,
                  dot: 'bg-red-500',
                  text: 'text-red-400',
                },
                {
                  label: 'Medium',
                  value: analytics.priorityDistribution.medium,
                  dot: 'bg-yellow-500',
                  text: 'text-yellow-400',
                },
                {
                  label: 'Low',
                  value: analytics.priorityDistribution.low,
                  dot: 'bg-blue-500',
                  text: 'text-blue-400',
                },
              ].map(({ label, value, dot, text }) => (
                <div key={label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className={`w-2 h-2 rounded-full ${dot}`} />
                    <span className="text-xs text-slate-400">{label}</span>
                  </div>
                  <span className={`text-sm font-bold ${text}`}>{value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick links */}
          <div className="grid grid-cols-2 gap-3">
            <Link
              href="/dashboard/tasks"
              className="bg-primary/[0.08] border border-primary/20 rounded-xl p-4 hover:bg-primary/15 transition-all duration-200 group text-center"
            >
              <CheckSquare className="w-5 h-5 text-primary mx-auto mb-1.5 group-hover:scale-110 transition-transform" />
              <p className="text-xs font-semibold text-white">Tasks</p>
            </Link>
            <Link
              href="/dashboard/analytics"
              className="bg-accent/[0.08] border border-accent/20 rounded-xl p-4 hover:bg-accent/15 transition-all duration-200 group text-center"
            >
              <BarChart3 className="w-5 h-5 text-accent mx-auto mb-1.5 group-hover:scale-110 transition-transform" />
              <p className="text-xs font-semibold text-white">Analytics</p>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
