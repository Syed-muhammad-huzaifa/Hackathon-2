import { redirect } from "next/navigation";
import { auth } from "@/lib/auth/auth";
import { headers } from "next/headers";
import { DashboardSidebar } from "@/components/layout/DashboardSidebar";
import { DashboardMobileNav } from "@/components/layout/DashboardMobileNav";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  let session = null;
  try {
    session = await auth.api.getSession({
      headers: await headers(),
    });
  } catch (error) {
    console.error("Failed to get session:", error);
  }

  if (!session) {
    redirect("/signin");
  }

  return (
    <div className="flex min-h-screen bg-[#0b0f14]">
      <DashboardSidebar
        userName={session.user.name}
        userEmail={session.user.email}
      />
      <div className="flex-1 min-w-0">
        <DashboardMobileNav />
        <main className="min-h-screen overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  );
}
