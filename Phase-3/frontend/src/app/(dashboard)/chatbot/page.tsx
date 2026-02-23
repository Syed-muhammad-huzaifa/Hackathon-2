"use client";

import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { authClient } from "@/lib/auth/auth-client";

type TokenResponse = { data?: { token?: string } };

export default function ChatbotPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  const domainKey = process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || "local-dev";

  const getAuthToken = useCallback(async () => {
    const tokenResult = (await authClient.token()) as TokenResponse | null;
    const token = tokenResult?.data?.token;

    if (!token) {
      throw new Error("Failed to get authentication token");
    }

    return token;
  }, []);

  const chatkitFetch = useCallback(
    async (input: RequestInfo | URL, init?: RequestInit) => {
      const token = await getAuthToken();
      const headers = new Headers(init?.headers);
      headers.set("Authorization", `Bearer ${token}`);
      return fetch(input, { ...init, headers });
    },
    [getAuthToken]
  );

  const { control, setThreadId } = useChatKit({
    api: {
      url: `${backendUrl}/api/chatkit/`,
      domainKey,
      fetch: chatkitFetch,
    },
    theme: "dark",
  });

  useEffect(() => {
    let mounted = true;

    const checkAuth = async () => {
      try {
        const session = await authClient.getSession();

        if (!mounted) {
          return;
        }

        if (!session?.data?.user?.id) {
          setError("Please sign in to use the chatbot");
        }
      } catch (err) {
        console.error("Chatbot authentication check error:", err);
        if (mounted) {
          setError("Failed to verify authentication");
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    void checkAuth();

    return () => {
      mounted = false;
    };
  }, []);

  const handleNewConversation = () => {
    void setThreadId(null);
  };

  return (
    <div className="min-h-screen bg-[#0b0f14]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Assistant</p>
            <h1 className="text-2xl sm:text-3xl font-semibold text-white mt-2">TaskAI Chat</h1>
          </div>
          {!isLoading && !error && (
            <Button variant="secondary" onClick={handleNewConversation}>
              New conversation
            </Button>
          )}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center min-h-[70vh]">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-zinc-400">Loading chat...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center min-h-[70vh]">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-8 h-8 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-white mb-2">Error</h2>
              <p className="text-zinc-400">{error}</p>
            </div>
          </div>
        ) : (
          <div className="glass rounded-3xl overflow-hidden flex flex-col min-h-[60vh] h-[calc(100vh-200px)] sm:h-[calc(100vh-180px)] max-h-[820px]">
            <div className="flex-1 min-h-0 p-3 sm:p-4">
              <ChatKit control={control} className="h-full w-full" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
