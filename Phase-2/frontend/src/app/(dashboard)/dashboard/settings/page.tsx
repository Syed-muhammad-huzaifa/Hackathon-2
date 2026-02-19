'use client';

/**
 * Settings Page
 * User profile, security, and preferences
 */

import { authClient } from '@/lib/auth/client';
import { Settings, User, Shield, Bell, Loader2, Mail, Calendar } from 'lucide-react';

function formatMemberDate(date: Date | string | undefined): string {
  if (!date) return '—';
  return new Date(date).toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
}

export default function SettingsPage() {
  const { data: session, isPending } = authClient.useSession();
  const user = session?.user;
  const initial = (user?.name || user?.email || 'U')[0].toUpperCase();

  if (isPending) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      {/* Header */}
      <div className="pt-2">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-slate-500 to-slate-700 flex items-center justify-center shadow-lg">
            <Settings className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Settings</h1>
        </div>
        <p className="text-slate-400 ml-12 text-sm">
          Manage your account and preferences
        </p>
      </div>

      {/* Profile Section */}
      <section className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-5 sm:p-6">
        <div className="flex items-center gap-2 mb-5 pb-4 border-b border-white/[0.06]">
          <User className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-semibold text-white">Profile</h2>
        </div>

        <div className="flex items-start gap-4 sm:gap-5">
          {/* Avatar */}
          <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xl sm:text-2xl font-bold shadow-xl shadow-primary/20 flex-shrink-0">
            {initial}
          </div>

          <div className="flex-1 space-y-3 sm:space-y-4">
            <div className="grid sm:grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-1.5">
                  <User className="w-3 h-3" />
                  Full Name
                </label>
                <div className="px-4 py-3 rounded-xl bg-white/[0.025] border border-white/[0.07] text-sm text-white">
                  {user?.name || <span className="text-slate-500">—</span>}
                </div>
              </div>
              <div>
                <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-1.5">
                  <Mail className="w-3 h-3" />
                  Email
                </label>
                <div className="px-4 py-3 rounded-xl bg-white/[0.025] border border-white/[0.07] text-sm text-white truncate">
                  {user?.email || <span className="text-slate-500">—</span>}
                </div>
              </div>
            </div>

            <div>
              <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-1.5">
                <Calendar className="w-3 h-3" />
                Member Since
              </label>
              <div className="px-4 py-3 rounded-xl bg-white/[0.025] border border-white/[0.07] text-sm text-slate-300">
                {formatMemberDate(user?.createdAt)}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-white/[0.05]">
          <p className="text-xs text-slate-600">
            Profile editing is coming in a future update.
          </p>
        </div>
      </section>

      {/* Security Section */}
      <section className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-5 sm:p-6">
        <div className="flex items-center gap-2 mb-5 pb-4 border-b border-white/[0.06]">
          <Shield className="w-4 h-4 text-blue-400" />
          <h2 className="text-sm font-semibold text-white">Security</h2>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between px-4 py-4 rounded-xl bg-white/[0.025] border border-white/[0.06]">
            <div>
              <p className="text-sm font-medium text-white">Password</p>
              <p className="text-xs text-slate-500 mt-0.5">
                Change your account password
              </p>
            </div>
            <span className="text-[10px] font-semibold px-2.5 py-1 rounded-full bg-slate-700/50 text-slate-400 border border-slate-600/30 flex-shrink-0">
              SOON
            </span>
          </div>

          <div className="flex items-center justify-between px-4 py-4 rounded-xl bg-white/[0.025] border border-white/[0.06]">
            <div>
              <p className="text-sm font-medium text-white">Two-Factor Auth</p>
              <p className="text-xs text-slate-500 mt-0.5">
                Add an extra layer of protection
              </p>
            </div>
            <span className="text-[10px] font-semibold px-2.5 py-1 rounded-full bg-slate-700/50 text-slate-400 border border-slate-600/30 flex-shrink-0">
              SOON
            </span>
          </div>

          <div className="flex items-center justify-between px-4 py-4 rounded-xl bg-white/[0.025] border border-white/[0.06]">
            <div>
              <p className="text-sm font-medium text-white">Active Sessions</p>
              <p className="text-xs text-slate-500 mt-0.5">
                Manage where you&apos;re signed in
              </p>
            </div>
            <span className="text-[10px] font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex-shrink-0">
              1 ACTIVE
            </span>
          </div>
        </div>
      </section>

      {/* Notifications Section */}
      <section className="bg-slate-900/60 backdrop-blur-xl border border-white/[0.07] rounded-2xl p-5 sm:p-6">
        <div className="flex items-center gap-2 mb-5 pb-4 border-b border-white/[0.06]">
          <Bell className="w-4 h-4 text-yellow-400" />
          <h2 className="text-sm font-semibold text-white">Notifications</h2>
        </div>

        <div className="space-y-3">
          {[
            {
              label: 'Task Reminders',
              desc: 'Get notified about upcoming tasks',
            },
            {
              label: 'Weekly Summary',
              desc: 'Receive a weekly productivity digest',
            },
            {
              label: 'Completion Alerts',
              desc: 'Notify when all daily tasks are done',
            },
          ].map(({ label, desc }) => (
            <div
              key={label}
              className="flex items-center justify-between px-4 py-4 rounded-xl bg-white/[0.025] border border-white/[0.06]"
            >
              <div>
                <p className="text-sm font-medium text-white">{label}</p>
                <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
              </div>
              {/* Disabled toggle visual */}
              <div
                className="relative w-9 h-5 rounded-full bg-slate-700 border border-white/10 flex-shrink-0 opacity-40 cursor-not-allowed"
                aria-hidden="true"
              >
                <div className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-slate-500 transition-transform duration-200" />
              </div>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-600 mt-4">
          Notification settings coming in a future update.
        </p>
      </section>

      {/* Danger Zone */}
      <section className="bg-red-950/20 backdrop-blur-xl border border-red-500/10 rounded-2xl p-5 sm:p-6">
        <h2 className="text-sm font-semibold text-red-400 mb-4">Danger Zone</h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-white">Delete Account</p>
            <p className="text-xs text-slate-500 mt-0.5">
              Permanently delete your account and all data
            </p>
          </div>
          <button
            disabled
            className="text-xs font-semibold px-4 py-2 rounded-lg border border-red-500/30 text-red-400/50 bg-red-500/5 cursor-not-allowed"
          >
            Delete
          </button>
        </div>
      </section>
    </div>
  );
}
