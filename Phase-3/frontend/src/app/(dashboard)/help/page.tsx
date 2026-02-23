"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function HelpPage() {
  const sections = [
    {
      title: "Getting Started",
      desc: "Learn the basics of managing tasks with natural language",
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      items: [
        "How to create a task using natural language",
        "Viewing and filtering your task list",
        "Marking tasks as complete",
        "Deleting or archiving tasks",
      ],
    },
    {
      title: "Natural Language Commands",
      desc: "Examples of commands you can use with the AI chatbot",
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      items: [
        '"Add a task to buy groceries tomorrow"',
        '"Show me all my pending tasks"',
        '"Mark the project proposal task as complete"',
        '"Delete all completed tasks from last week"',
      ],
    },
    {
      title: "Analytics & Insights",
      desc: "Understanding your productivity metrics and patterns",
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      items: [
        "View task status distribution with pie charts",
        "Track weekly completion trends",
        "Analyze tasks by category",
        "Monitor your productivity over time",
      ],
    },
    {
      title: "Task History",
      desc: "Keep track of completed and deleted tasks",
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      items: [
        "Access your complete task history",
        "Review completed tasks with timestamps",
        "See deleted tasks for reference",
        "Filter history by date and action type",
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-[#0b0f14] p-4 sm:p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-white mb-2">Help & Documentation</h1>
          <p className="text-zinc-400">Learn how to use TaskAI effectively</p>
        </div>

        <div className="space-y-6">
          {sections.map((section) => (
            <Card key={section.title} glass className="p-5 sm:p-6">
              <div className="flex items-start gap-4 mb-4">
                <div className="w-11 h-11 sm:w-12 sm:h-12 rounded-xl bg-white/10 border border-white/10 flex items-center justify-center shrink-0 shadow-[0_12px_30px_rgba(79,124,255,0.2)]">
                  {section.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-white mb-1">{section.title}</h3>
                  <p className="text-sm text-zinc-400">{section.desc}</p>
                </div>
              </div>
              <ul className="space-y-2 sm:ml-16">
                {section.items.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-sm text-zinc-300">
                    <svg className="w-4 h-4 text-blue-300 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </Card>
          ))}

          {/* Contact Support */}
          <Card glass className="p-5 sm:p-6">
            <div className="text-center">
              <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-white/10 border border-white/10 flex items-center justify-center mx-auto mb-4 shadow-[0_12px_30px_rgba(79,124,255,0.2)]">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Need More Help?</h3>
              <p className="text-zinc-400 text-sm mb-4">
                Can't find what you're looking for? Our support team is here to help.
              </p>
              <Button variant="secondary" disabled>
                Contact Support
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
