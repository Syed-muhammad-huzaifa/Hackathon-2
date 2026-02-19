/**
 * Premium Landing Page — TaskFlow
 * 7 sections: Hero · Trust · Features · How It Works · Stats · Testimonials · CTA
 */

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import {
  CheckCircle2,
  Zap,
  Shield,
  BarChart3,
  Bell,
  Sparkles,
  ArrowRight,
  Users,
  Star,
  Check,
  Circle,
  TrendingUp,
  Target,
  Layers,
} from 'lucide-react';

/* ─── Feature Card ───────────────────────────────────────────────── */
function FeatureCard({
  icon: Icon,
  title,
  desc,
  gradient,
  shadow,
  large = false,
  delay = 0,
}: {
  icon: React.ElementType;
  title: string;
  desc: string;
  gradient: string;
  shadow: string;
  large?: boolean;
  delay?: number;
}) {
  return (
    <div
      className={`bg-slate-900/60 backdrop-blur-2xl border border-white/[0.07] rounded-2xl p-6 sm:p-8 space-y-4 hover:border-white/15 hover:-translate-y-1 transition-all duration-300 cursor-default group animate-slide-up ${
        large ? 'sm:col-span-2' : ''
      }`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div
        className={`w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg ${shadow} group-hover:scale-110 transition-transform duration-300`}
      >
        <Icon className="w-6 h-6 sm:w-7 sm:h-7 text-white" aria-hidden="true" />
      </div>
      <h3 className="text-xl sm:text-2xl font-bold text-white">{title}</h3>
      <p className="text-slate-400 leading-relaxed text-sm sm:text-base">{desc}</p>
    </div>
  );
}

/* ─── Step Card ──────────────────────────────────────────────────── */
function StepCard({
  number,
  icon: Icon,
  title,
  desc,
  delay = 0,
}: {
  number: string;
  icon: React.ElementType;
  title: string;
  desc: string;
  delay?: number;
}) {
  return (
    <div
      className="flex flex-col items-center text-center gap-4 animate-slide-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="relative">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 border border-primary/30 flex items-center justify-center shadow-lg shadow-primary/10">
          <Icon className="w-7 h-7 text-primary" aria-hidden="true" />
        </div>
        <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-[10px] font-black text-white shadow-lg">
          {number}
        </div>
      </div>
      <div>
        <h3 className="text-lg font-bold text-white mb-1.5">{title}</h3>
        <p className="text-slate-400 text-sm leading-relaxed max-w-[200px] mx-auto">{desc}</p>
      </div>
    </div>
  );
}

/* ─── Testimonial Card ───────────────────────────────────────────── */
function TestimonialCard({
  quote,
  name,
  role,
  company,
  avatarGradient,
  delay = 0,
}: {
  quote: string;
  name: string;
  role: string;
  company: string;
  avatarGradient: string;
  delay?: number;
}) {
  return (
    <div
      className="bg-slate-900/60 backdrop-blur-2xl border border-white/[0.07] rounded-2xl p-6 sm:p-8 space-y-4 hover:border-white/15 hover:-translate-y-0.5 transition-all duration-300 animate-slide-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((s) => (
          <Star key={s} className="w-4 h-4 fill-accent text-accent" aria-hidden="true" />
        ))}
      </div>
      <p className="text-slate-300 leading-relaxed text-sm sm:text-base">{quote}</p>
      <div className="flex items-center gap-3 pt-2">
        <div
          className={`w-10 h-10 rounded-full bg-gradient-to-br ${avatarGradient} flex items-center justify-center text-white text-sm font-bold flex-shrink-0`}
        >
          {name[0]}
        </div>
        <div>
          <div className="font-semibold text-white text-sm">{name}</div>
          <div className="text-xs text-slate-500">
            {role} · {company}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── Page ───────────────────────────────────────────────────────── */
export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#020617] overflow-x-hidden">
      <Header />

      <main className="flex-1">

        {/* ═══════════════════════════════════════════════════════════
            SECTION 1 — HERO
        ═══════════════════════════════════════════════════════════ */}
        <section className="relative min-h-[90vh] sm:min-h-screen flex items-center justify-center pt-24 pb-16 sm:pt-28 sm:pb-20 overflow-hidden">
          {/* Animated gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-[#020617] via-[#0a0e27] to-[#020617]" />
          <div className="absolute inset-0 [background:radial-gradient(circle_at_30%_20%,oklch(0.628_0.194_293.498_/_0.15)_0%,transparent_50%),radial-gradient(circle_at_70%_80%,oklch(0.588_0.233_263.711_/_0.12)_0%,transparent_50%)] animate-gradient" />

          {/* Grid overlay */}
          <div className="absolute inset-0 [background-image:linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] [background-size:64px_64px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />

          {/* Floating orbs */}
          <div className="absolute top-1/4 left-[10%] w-72 h-72 bg-primary/20 rounded-full blur-[120px] animate-blob" />
          <div className="absolute bottom-1/3 right-[15%] w-96 h-96 bg-secondary/15 rounded-full blur-[120px] animate-blob" style={{ animationDelay: '4s' }} />

          <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="max-w-5xl mx-auto text-center space-y-8 sm:space-y-10 animate-fade-in">
              {/* Trust badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.04] border border-white/[0.08] backdrop-blur-xl text-sm font-medium text-slate-300 shadow-lg">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs sm:text-sm">Trusted by 10,000+ professionals worldwide</span>
              </div>

              {/* Main headline */}
              <div className="space-y-4 sm:space-y-6">
                <h1 className="text-4xl sm:text-6xl md:text-7xl lg:text-8xl font-black leading-[1.05] tracking-tight">
                  <span className="block text-white mb-2">Productivity</span>
                  <span className="block bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent animate-gradient">
                    Reimagined
                  </span>
                </h1>
                <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-slate-400 leading-relaxed max-w-3xl mx-auto px-4">
                  The most beautiful way to organize your work. Powerful analytics, seamless collaboration, and stunning design — all in one place.
                </p>
              </div>

              {/* CTA buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 pt-4">
                <Button
                  size="lg"
                  asChild
                  className="group w-full sm:w-auto bg-gradient-to-r from-primary via-secondary to-accent hover:opacity-90 hover:scale-[1.02] transition-all duration-300 text-base sm:text-lg px-8 sm:px-10 py-6 sm:py-7 rounded-2xl shadow-2xl shadow-primary/50 cursor-pointer font-bold"
                >
                  <Link href="/sign-up">
                    Start Free Today
                    <ArrowRight
                      className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform"
                      aria-hidden="true"
                    />
                  </Link>
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  asChild
                  className="w-full sm:w-auto text-base sm:text-lg px-8 sm:px-10 py-6 sm:py-7 rounded-2xl border-white/20 hover:bg-white/[0.08] hover:border-white/30 transition-all duration-300 cursor-pointer font-bold backdrop-blur-xl"
                >
                  <Link href="/sign-in">Sign In</Link>
                </Button>
              </div>

              {/* Social proof with avatars */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-6">
                <div className="flex -space-x-3">
                  {['from-violet-500 to-purple-600', 'from-blue-500 to-cyan-600', 'from-pink-500 to-rose-600', 'from-emerald-500 to-teal-600', 'from-amber-500 to-orange-600'].map(
                    (gradient, i) => (
                      <div
                        key={i}
                        className={`w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gradient-to-br ${gradient} border-3 border-[#020617] flex items-center justify-center text-white text-sm font-bold shadow-lg`}
                      >
                        {['S', 'A', 'M', 'J', 'L'][i]}
                      </div>
                    )
                  )}
                </div>
                <div className="text-sm sm:text-base text-slate-400">
                  Join <span className="text-white font-bold">10,000+</span> users achieving more every day
                </div>
              </div>

              {/* Feature highlights */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 pt-8 max-w-3xl mx-auto">
                {[
                  { icon: CheckCircle2, text: 'Free Forever Plan' },
                  { icon: Shield, text: 'Bank-Level Security' },
                  { icon: Zap, text: 'Lightning Fast' },
                ].map(({ icon: Icon, text }) => (
                  <div
                    key={text}
                    className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06] backdrop-blur-xl"
                  >
                    <Icon className="w-4 h-4 text-primary flex-shrink-0" aria-hidden="true" />
                    <span className="text-xs sm:text-sm text-slate-300 font-medium">{text}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Scroll indicator */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce hidden sm:block">
            <div className="w-6 h-10 rounded-full border-2 border-white/20 flex items-start justify-center p-2">
              <div className="w-1.5 h-3 bg-white/40 rounded-full" />
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 2 — TRUST BAR
        ═══════════════════════════════════════════════════════════ */}
        <section className="relative py-12 border-y border-white/[0.06] overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/[0.03] to-transparent" />
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <p className="text-center text-xs font-semibold text-slate-600 uppercase tracking-widest mb-8">
              Trusted by innovative teams worldwide
            </p>
            {/* Scrolling company names */}
            <div className="relative overflow-hidden">
              <div className="flex gap-12 animate-marquee whitespace-nowrap">
                {['Stripe', 'Vercel', 'Linear', 'Notion', 'Figma', 'Loom', 'Intercom', 'Segment', 'Amplitude', 'Retool',
                  'Stripe', 'Vercel', 'Linear', 'Notion', 'Figma', 'Loom', 'Intercom', 'Segment', 'Amplitude', 'Retool'].map(
                  (name, i) => (
                    <span
                      key={i}
                      className="text-slate-600 font-bold text-lg hover:text-slate-400 transition-colors cursor-default select-none"
                    >
                      {name}
                    </span>
                  )
                )}
              </div>
              {/* Fade edges */}
              <div className="absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-[#020617] to-transparent pointer-events-none" />
              <div className="absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-[#020617] to-transparent pointer-events-none" />
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 3 — FEATURES BENTO GRID
        ═══════════════════════════════════════════════════════════ */}
        <section className="relative py-24 sm:py-32 overflow-hidden">
          <div className="absolute inset-0 [background:radial-gradient(at_50%_0%,oklch(0.628_0.194_293.498_/_0.08)_0px,transparent_60%)]" />
          <div className="absolute inset-0 [background-image:linear-gradient(rgba(255,255,255,0.025)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.025)_1px,transparent_1px)] [background-size:60px_60px]" />

          <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            {/* Section header */}
            <div className="text-center mb-16 space-y-4 animate-slide-up">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08] text-xs font-semibold text-slate-400 uppercase tracking-widest">
                <Layers className="w-3.5 h-3.5 text-primary" />
                Features
              </div>
              <h2 className="text-4xl sm:text-5xl font-extrabold text-white">
                Everything you need to
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  {' '}excel
                </span>
              </h2>
              <p className="text-lg text-slate-400 max-w-xl mx-auto">
                Powerful features designed for modern professionals who demand the best.
              </p>
            </div>

            {/* Bento grid */}
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 max-w-6xl mx-auto">
              <FeatureCard
                icon={BarChart3}
                title="Advanced Analytics"
                desc="Visualize your productivity with beautiful charts, trend lines, and AI-powered insights that help you work smarter every day."
                gradient="from-primary to-secondary"
                shadow="shadow-primary/30"
                large
                delay={0}
              />
              <FeatureCard
                icon={CheckCircle2}
                title="Intuitive Interface"
                desc="Create and manage tasks in seconds with our beautifully crafted, distraction-free interface."
                gradient="from-emerald-500 to-teal-500"
                shadow="shadow-emerald-500/30"
                delay={100}
              />
              <FeatureCard
                icon={Shield}
                title="Enterprise Security"
                desc="Bank-level encryption keeps your data safe. SOC 2 certified. GDPR compliant."
                gradient="from-blue-500 to-indigo-500"
                shadow="shadow-blue-500/30"
                delay={150}
              />
              <FeatureCard
                icon={Bell}
                title="Smart Reminders"
                desc="Never miss a deadline. Intelligent notifications adapt to your work patterns."
                gradient="from-amber-500 to-orange-500"
                shadow="shadow-amber-500/30"
                delay={200}
              />
              <FeatureCard
                icon={Zap}
                title="Lightning Fast"
                desc="Sub-50ms response times ensure the app never slows you down, on any device."
                gradient="from-pink-500 to-rose-500"
                shadow="shadow-pink-500/30"
                delay={250}
              />
              <FeatureCard
                icon={Users}
                title="Team Collaboration"
                desc="Real-time sync across your whole team. Assign, comment, and track progress together."
                gradient="from-violet-500 to-purple-600"
                shadow="shadow-violet-500/30"
                delay={300}
              />
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 4 — HOW IT WORKS
        ═══════════════════════════════════════════════════════════ */}
        <section className="relative py-24 sm:py-32 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/[0.03] to-transparent" />

          <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="text-center mb-16 space-y-4 animate-slide-up">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08] text-xs font-semibold text-slate-400 uppercase tracking-widest">
                <Target className="w-3.5 h-3.5 text-accent" />
                How It Works
              </div>
              <h2 className="text-4xl sm:text-5xl font-extrabold text-white">
                Up and running in
                <span className="bg-gradient-to-r from-secondary to-accent bg-clip-text text-transparent">
                  {' '}3 steps
                </span>
              </h2>
              <p className="text-lg text-slate-400 max-w-xl mx-auto">
                Getting started takes less than 60 seconds. No credit card required.
              </p>
            </div>

            {/* Steps */}
            <div className="relative max-w-4xl mx-auto">
              {/* Connecting line (desktop) */}
              <div className="hidden md:block absolute top-8 left-[16.67%] right-[16.67%] h-px bg-gradient-to-r from-primary/30 via-secondary/50 to-accent/30" />

              <div className="grid md:grid-cols-3 gap-10 md:gap-8">
                <StepCard
                  number="1"
                  icon={Circle}
                  title="Create Your Account"
                  desc="Sign up in seconds with just your email. No credit card needed."
                  delay={0}
                />
                <StepCard
                  number="2"
                  icon={CheckCircle2}
                  title="Add Your Tasks"
                  desc="Create tasks, set priorities, and organize your work the way you think."
                  delay={150}
                />
                <StepCard
                  number="3"
                  icon={TrendingUp}
                  title="Track & Achieve"
                  desc="Watch your productivity soar with real-time analytics and insights."
                  delay={300}
                />
              </div>
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 5 — STATS
        ═══════════════════════════════════════════════════════════ */}
        <section className="relative py-20 sm:py-28 overflow-hidden">
          <div className="absolute inset-0 [background:radial-gradient(at_50%_50%,oklch(0.628_0.194_293.498_/_0.1)_0px,transparent_70%)]" />
          <div className="absolute inset-0 border-y border-white/[0.06]" />

          <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 sm:gap-12 max-w-5xl mx-auto text-center">
              {[
                { value: '10K+', label: 'Active Users', gradient: 'from-primary to-secondary', delay: 0 },
                { value: '1M+', label: 'Tasks Completed', gradient: 'from-secondary to-accent', delay: 100 },
                { value: '99.9%', label: 'Uptime SLA', gradient: 'from-accent to-primary', delay: 200 },
                { value: '4.9★', label: 'Average Rating', gradient: 'from-amber-400 to-orange-500', delay: 300 },
              ].map(({ value, label, gradient, delay }) => (
                <div
                  key={label}
                  className="space-y-2 animate-slide-up"
                  style={{ animationDelay: `${delay}ms` }}
                >
                  <div
                    className={`text-4xl sm:text-5xl md:text-6xl font-black bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}
                  >
                    {value}
                  </div>
                  <div className="text-slate-400 font-medium text-sm sm:text-base">{label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 6 — TESTIMONIALS
        ═══════════════════════════════════════════════════════════ */}
        <section className="relative py-24 sm:py-32 overflow-hidden">
          <div className="absolute inset-0 bg-[#040812]" />
          <div className="absolute inset-0 [background-image:linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] [background-size:60px_60px]" />
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/8 rounded-full blur-[120px] pointer-events-none" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/8 rounded-full blur-[120px] pointer-events-none" />

          <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="text-center mb-16 space-y-4 animate-slide-up">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08] text-xs font-semibold text-slate-400 uppercase tracking-widest">
                <Star className="w-3.5 h-3.5 text-accent fill-accent" />
                Testimonials
              </div>
              <h2 className="text-4xl sm:text-5xl font-extrabold text-white">
                Loved by
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  {' '}professionals
                </span>
              </h2>
              <p className="text-lg text-slate-400 max-w-xl mx-auto">
                Join thousands of users who have already transformed their productivity.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-5 sm:gap-6 max-w-6xl mx-auto">
              <TestimonialCard
                quote="TaskFlow completely changed how I manage projects. The analytics alone saved me 3 hours a week. The UI is absolutely stunning."
                name="Sarah Johnson"
                role="Product Manager"
                company="Vercel"
                avatarGradient="from-violet-500 to-purple-600"
                delay={0}
              />
              <TestimonialCard
                quote="I've tried every todo app out there. TaskFlow is the first one that actually stuck. The priority system is genius."
                name="Marcus Chen"
                role="Lead Engineer"
                company="Stripe"
                avatarGradient="from-blue-500 to-cyan-600"
                delay={100}
              />
              <TestimonialCard
                quote="Our entire team switched in a week. The collaboration features are seamless and the design is world-class."
                name="Alex Rivera"
                role="Design Director"
                company="Linear"
                avatarGradient="from-emerald-500 to-teal-600"
                delay={200}
              />
            </div>
          </div>
        </section>

        {/* ═══════════════════════════════════════════════════════════
            SECTION 7 — FINAL CTA
        ═══════════════════════════════════════════════════════════ */}
        <section className="relative py-20 sm:py-28 md:py-32 overflow-hidden">
          {/* Animated background */}
          <div className="absolute inset-0 bg-gradient-to-br from-[#020617] via-[#0a0e27] to-[#020617]" />
          <div className="absolute inset-0 [background:radial-gradient(circle_at_50%_50%,oklch(0.628_0.194_293.498_/_0.18)_0%,transparent_60%)] animate-gradient" />

          {/* Grid pattern */}
          <div className="absolute inset-0 [background-image:linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] [background-size:48px_48px]" />

          {/* Floating orbs */}
          <div className="absolute top-1/4 left-[10%] w-80 h-80 bg-primary/15 rounded-full blur-[100px] animate-blob" />
          <div className="absolute bottom-1/4 right-[10%] w-96 h-96 bg-secondary/12 rounded-full blur-[100px] animate-blob" style={{ animationDelay: '3s' }} />

          <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="max-w-4xl mx-auto">
              {/* Main CTA card */}
              <div className="relative bg-gradient-to-br from-slate-900/80 to-slate-900/60 backdrop-blur-2xl border border-white/[0.1] rounded-3xl sm:rounded-[2rem] p-8 sm:p-12 md:p-16 shadow-2xl overflow-hidden animate-slide-up">
                {/* Inner glow effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.08] via-transparent to-secondary/[0.08] pointer-events-none" />

                {/* Decorative elements */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-[80px] pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent/10 rounded-full blur-[80px] pointer-events-none" />

                <div className="relative space-y-6 sm:space-y-8 text-center">
                  {/* Badge */}
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 backdrop-blur-xl">
                    <Sparkles className="w-4 h-4 text-emerald-400" aria-hidden="true" />
                    <span className="text-xs sm:text-sm font-semibold text-emerald-400">
                      Free Forever · No Credit Card Required
                    </span>
                  </div>

                  {/* Headline */}
                  <div className="space-y-4">
                    <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black text-white leading-tight">
                      Ready to transform
                      <br />
                      <span className="bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent animate-gradient">
                        your productivity?
                      </span>
                    </h2>
                    <p className="text-base sm:text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed px-4">
                      Join 10,000+ professionals who have already elevated their workflow. Start free today.
                    </p>
                  </div>

                  {/* CTA Buttons */}
                  <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 pt-4">
                    <Button
                      size="lg"
                      asChild
                      className="group w-full sm:w-auto bg-gradient-to-r from-primary via-secondary to-accent hover:opacity-90 hover:scale-[1.02] transition-all duration-300 text-base sm:text-lg px-10 sm:px-12 py-6 sm:py-7 rounded-2xl shadow-2xl shadow-primary/50 cursor-pointer font-bold"
                    >
                      <Link href="/sign-up">
                        Get Started Free
                        <ArrowRight
                          className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform"
                          aria-hidden="true"
                        />
                      </Link>
                    </Button>
                    <Button
                      size="lg"
                      variant="ghost"
                      asChild
                      className="w-full sm:w-auto text-base sm:text-lg px-10 sm:px-12 py-6 sm:py-7 rounded-2xl hover:bg-white/[0.08] transition-all duration-300 cursor-pointer text-slate-300 hover:text-white font-bold"
                    >
                      <Link href="/sign-in">
                        Sign In
                        <ArrowRight className="ml-2 w-4 h-4" aria-hidden="true" />
                      </Link>
                    </Button>
                  </div>

                  {/* Trust indicators */}
                  <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-3 pt-6 text-sm text-slate-500">
                    {[
                      { icon: Check, text: 'No credit card required' },
                      { icon: Check, text: 'Free forever plan' },
                      { icon: Check, text: 'Cancel anytime' },
                    ].map(({ icon: Icon, text }) => (
                      <span key={text} className="flex items-center gap-2">
                        <Icon className="w-4 h-4 text-emerald-500 flex-shrink-0" strokeWidth={3} />
                        <span className="text-xs sm:text-sm">{text}</span>
                      </span>
                    ))}
                  </div>

                  {/* Stats row */}
                  <div className="grid grid-cols-3 gap-4 sm:gap-8 pt-8 border-t border-white/[0.06]">
                    {[
                      { value: '10K+', label: 'Active Users' },
                      { value: '99.9%', label: 'Uptime' },
                      { value: '4.9★', label: 'Rating' },
                    ].map(({ value, label }) => (
                      <div key={label} className="space-y-1">
                        <div className="text-2xl sm:text-3xl font-black bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                          {value}
                        </div>
                        <div className="text-xs sm:text-sm text-slate-500 font-medium">{label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>

      <Footer />
    </div>
  );
}
