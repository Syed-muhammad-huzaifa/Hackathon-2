/**
 * Tasks Management Page
 * Full task CRUD with status/priority overview
 */

import { auth } from '@/lib/auth/server';
import { redirect } from 'next/navigation';
import { headers } from 'next/headers';
import { TaskList } from '@/components/tasks/task-list';
import type { Task } from '@/types/task';
import { CheckSquare, Circle, Clock, CheckCircle2 } from 'lucide-react';

async function getPageData() {
  const headersList = await headers();
  const session = await auth.api.getSession({ headers: headersList });
  if (!session?.user) redirect('/sign-in');

  const tokenResponse = await auth.api.getToken({ headers: headersList });
  let tasks: Task[] = [];
  if (tokenResponse?.token) {
    try {
      const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const res = await fetch(`${apiUrl}/api/${session.user.id}/tasks`, {
        headers: {
          Authorization: `Bearer ${tokenResponse.token}`,
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
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

export default async function TasksPage() {
  const { user, tasks } = await getPageData();
  const nonDeleted = tasks.filter((t) => t.status !== 'deleted');
  const pending = nonDeleted.filter((t) => t.status === 'pending').length;
  const inProgress = nonDeleted.filter((t) => t.status === 'in-progress').length;
  const completed = nonDeleted.filter((t) => t.status === 'completed').length;

  const statusCards = [
    {
      label: 'Pending',
      value: pending,
      icon: Circle,
      color: 'text-slate-300',
      bg: 'bg-slate-500/[0.08] border-slate-500/20',
      iconColor: 'text-slate-400',
    },
    {
      label: 'In Progress',
      value: inProgress,
      icon: Clock,
      color: 'text-blue-400',
      bg: 'bg-blue-500/[0.08] border-blue-500/20',
      iconColor: 'text-blue-400',
    },
    {
      label: 'Completed',
      value: completed,
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/[0.08] border-emerald-500/20',
      iconColor: 'text-emerald-400',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page header */}
      <div className="pt-2">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/25">
            <CheckSquare className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Tasks</h1>
        </div>
        <p className="text-slate-400 ml-12 text-sm">
          Create, manage, and track all your tasks
        </p>
      </div>

      {/* Status overview cards */}
      {nonDeleted.length > 0 && (
        <div className="grid grid-cols-3 gap-3 sm:gap-4">
          {statusCards.map(({ label, value, icon: Icon, color, bg, iconColor }) => (
            <div
              key={label}
              className={`rounded-2xl border p-4 sm:p-5 ${bg} flex items-center gap-3 sm:gap-4`}
            >
              <div className="w-9 h-9 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0">
                <Icon className={`w-4 h-4 ${iconColor}`} aria-hidden="true" />
              </div>
              <div>
                <p className={`text-xl sm:text-2xl font-bold ${color}`}>{value}</p>
                <p className="text-xs text-slate-500 mt-0.5 hidden sm:block">{label}</p>
                <p className="text-[10px] text-slate-500 mt-0.5 sm:hidden">{label}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Task list */}
      <div className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-4 sm:p-6">
        <TaskList initialTasks={nonDeleted} userId={user.id} />
      </div>
    </div>
  );
}
