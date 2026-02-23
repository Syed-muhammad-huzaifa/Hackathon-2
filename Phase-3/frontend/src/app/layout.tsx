import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "TaskAI — Conversational Task Manager",
  description:
    "Manage your tasks through natural language with AI-powered chat interface.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="afterInteractive"
        />
      </head>
      <body className="font-sans antialiased bg-[#0b0f14] text-white">
        {children}
      </body>
    </html>
  );
}
