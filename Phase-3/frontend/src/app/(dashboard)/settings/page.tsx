"use client";

import { useState } from "react";
import { useSession, signOut } from "@/lib/auth/auth-client";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function SettingsPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const handleSignOut = async () => {
    setIsLoading(true);
    await signOut();
    router.push("/");
    router.refresh();
  };

  return (
    <div className="min-h-screen bg-[#0b0f14] p-4 sm:p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-white mb-2">Settings</h1>
          <p className="text-zinc-400">Manage your account and preferences</p>
        </div>

        <div className="space-y-6">
          {/* Profile Section */}
          <Card glass className="p-5 sm:p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Profile</h3>
            <div className="space-y-4">
              <Input
                label="Name"
                type="text"
                value={session?.user?.name ?? ""}
                placeholder="Your name"
                disabled
              />
              <Input
                label="Email"
                type="email"
                value={session?.user?.email ?? ""}
                placeholder="your@email.com"
                disabled
              />
              <p className="text-xs text-zinc-500">
                Profile information is managed through your authentication provider.
              </p>
            </div>
          </Card>

          {/* Preferences Section */}
          <Card glass className="p-5 sm:p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Preferences</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white">Email notifications</p>
                  <p className="text-xs text-zinc-400">Receive updates about your tasks</p>
                </div>
                <button
                  onClick={() => setEmailNotifications(!emailNotifications)}
                  className={`w-11 h-6 rounded-full relative transition-colors ${
                    emailNotifications ? "bg-blue-500" : "bg-zinc-700"
                  }`}
                >
                  <span
                    className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                      emailNotifications ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white">Task reminders</p>
                  <p className="text-xs text-zinc-400">Get reminded about upcoming tasks</p>
                </div>
                <button className="w-11 h-6 rounded-full bg-zinc-700 relative transition-colors">
                  <span className="absolute left-1 top-1 w-4 h-4 rounded-full bg-white transition-transform" />
                </button>
              </div>
            </div>
          </Card>

          {/* Security Section */}
          <Card glass className="p-5 sm:p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Security</h3>
            <div className="space-y-3">
              <Button variant="secondary" className="w-full justify-start" disabled>
                Change password
              </Button>
              <Button
                variant="destructive"
                className="w-full justify-start"
                onClick={handleSignOut}
                isLoading={isLoading}
              >
                {isLoading ? "Signing out..." : "Sign out"}
              </Button>
            </div>
          </Card>

          {/* Danger Zone */}
          <Card glass className="p-5 sm:p-6 border-red-500/20">
            <h3 className="text-lg font-semibold text-red-400 mb-4">Danger Zone</h3>
            <div className="space-y-3">
              <p className="text-sm text-zinc-400">
                Once you delete your account, there is no going back. Please be certain.
              </p>
              <Button variant="destructive" className="w-full" disabled>
                Delete account
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
