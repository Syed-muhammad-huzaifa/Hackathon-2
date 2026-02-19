/**
 * Analytics Page
 * Full productivity analytics with charts and KPI cards
 */

import { auth } from '@/lib/auth/server';
import { redirect } from 'next/navigation';
import { headers } from 'next/headers';
import { StatusChart } from '@/components/analytics/status-chart';
import { PriorityChart } from '@/components/analytics/priority-chart';
import { TrendChart } from '@/components/analytics/trend-chart';
import { computeAnalytics } from '@/lib/schemas/task';
import type { Task } from '@/types/task';
import { BarChart3, TrendingUp, Target, Award, Zap } from 'lucide-react';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

async function getPageData() {
  const headersList = await headers();
  const session = await auth.api.getSession({ headers: headersList });
  if (!session?.user) redirect('/sign-in');

  const tokenResponse = await auth.api.getToken({ headers: headersList });
  let tasks: Task[] = [];
  if (tokenResponse?.token) {
    try {
      const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
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

export default async function AnalyticsPage() {
  const { tasks } = await getPageData();
  const analytics = computeAnalytics(tasks);
  const nonDeleted = tasks.filter((t) => t.status !== 'deleted');

  const completionRate =
    nonDeleted.length > 0
      ? Math.round((analytics.statusDistribution.completed / nonDeleted.length) * 100)
      : 0;

  const highPriorityDone = tasks.filter(
    (t) => t.priority === 'high' && t.status === 'completed'
  ).length;

  const completedThisWeek = analytics.completionTrend
    .slice(-7)
    .reduce((sum, d) => sum + d.completed, 0);

  const avgPerDay =
    nonDeleted.length > 0 ? (completedThisWeek / 7).toFixed(1) : '0';

  const bestDay = analytics.completionTrend.reduce(
    (best, d) => (d.completed > best.completed ? d : best),
    { date: '', completed: 0 }
  );

  const kpis = [
    {
      label: 'Completion Rate',
      value: `${completionRate}%`,
      desc: 'of all tasks finished',
      icon: Target,
      gradient: 'from-violet-500 to-purple-600',
      shadow: 'shadow-purple-500/20',
    },
    {
      label: 'This Week',
      value: completedThisWeek,
      desc: 'tasks completed',
      icon: TrendingUp,
      gradient: 'from-emerald-500 to-green-600',
      shadow: 'shadow-emerald-500/20',
    },
    {
      label: 'Daily Average',
      value: avgPerDay,
      desc: 'tasks per day',
      icon: BarChart3,
      gradient: 'from-blue-500 to-cyan-600',
      shadow: 'shadow-blue-500/20',
    },
    {
      label: 'High Priority Done',
      value: highPriorityDone,
      desc: 'high-priority completed',
      icon: Award,
      gradient: 'from-amber-500 to-orange-600',
      shadow: 'shadow-amber-500/20',
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="pt-2">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent to-secondary flex items-center justify-center shadow-lg shadow-accent/25">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Analytics</h1>
        </div>
        <p className="text-slate-400 ml-12 text-sm">
          Track your productivity trends and task insights
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {kpis.map(({ label, value, desc, icon: Icon, gradient, shadow }) => (
          <div
            key={label}
            className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-5 hover:border-white/15 hover:-translate-y-0.5 transition-all duration-300"
          >
            <div
              className={`w-10 h-10 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg ${shadow} mb-4`}
            >
              <Icon className="w-5 h-5 text-white" aria-hidden="true" />
            </div>
            <p className="text-3xl font-bold text-white">{value}</p>
            <p className="text-sm font-medium text-slate-300 mt-1">{label}</p>
            <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
          </div>
        ))}
      </div>

      {nonDeleted.length === 0 ? (
        /* Empty state */
        <div className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-16 text-center">
          <div className="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="w-8 h-8 text-slate-600" />
          </div>
          <p className="text-white font-semibold text-lg">No data yet</p>
          <p className="text-slate-500 text-sm mt-1 max-w-xs mx-auto">
            Create and complete some tasks to start seeing your analytics here.
          </p>
        </div>
      ) : (
        <>
          {/* Best day callout */}
          {bestDay.completed > 0 && (
            <div className="bg-gradient-to-r from-primary/10 via-secondary/10 to-accent/10 border border-primary/20 rounded-2xl p-5 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0 shadow-lg shadow-primary/20">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">
                  Best day:{' '}
                  <span className="text-primary">
                    {new Date(bestDay.date).toLocaleDateString('en-US', {
                      weekday: 'long',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </span>
                </p>
                <p className="text-xs text-slate-400 mt-0.5">
                  You completed{' '}
                  <span className="text-white font-semibold">{bestDay.completed}</span>{' '}
                  {bestDay.completed === 1 ? 'task' : 'tasks'} — your most productive day!
                </p>
              </div>
            </div>
          )}

          {/* Charts row 1 */}
          <div className="grid lg:grid-cols-2 gap-6">
            <StatusChart data={analytics.statusDistribution} />
            <PriorityChart data={analytics.priorityDistribution} />
          </div>

          {/* Trend chart */}
          <TrendChart data={analytics.completionTrend} />

          {/* Summary table */}
          <div className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-5 sm:p-6">
            <h3 className="text-base font-semibold text-white mb-4">Summary</h3>
            <div className="grid sm:grid-cols-3 gap-4">
              {[
                {
                  label: 'Total Created',
                  value: nonDeleted.length,
                  sub: 'all time',
                  color: 'text-white',
                },
                {
                  label: 'Total Completed',
                  value: analytics.statusDistribution.completed,
                  sub: `${completionRate}% rate`,
                  color: 'text-emerald-400',
                },
                {
                  label: 'Still Active',
                  value:
                    analytics.statusDistribution.pending +
                    analytics.statusDistribution['in-progress'],
                  sub: 'pending + in progress',
                  color: 'text-blue-400',
                },
              ].map(({ label, value, sub, color }) => (
                <div
                  key={label}
                  className="px-4 py-4 rounded-xl bg-white/[0.025] border border-white/[0.05] text-center"
                >
                  <p className={`text-3xl font-bold ${color}`}>{value}</p>
                  <p className="text-sm text-slate-300 font-medium mt-1">{label}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{sub}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
