import { Sidebar } from '@/components/layout/sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#020617]">
      {/* Ambient background */}
      <div className="fixed inset-0 [background:radial-gradient(at_80%_20%,oklch(0.628_0.194_293.498_/_0.08)_0px,transparent_50%),radial-gradient(at_20%_80%,oklch(0.588_0.233_263.711_/_0.08)_0px,transparent_50%)] pointer-events-none" />

      <Sidebar />

      {/* Content area — offset by sidebar width on large screens */}
      <div className="lg:ml-64 min-h-screen flex flex-col relative">
        <main className="flex-1 pt-16 lg:pt-0 p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto w-full">
          {children}
        </main>
      </div>
    </div>
  );
}
