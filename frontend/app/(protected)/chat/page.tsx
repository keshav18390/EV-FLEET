"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User as UserIcon, Loader2, Sparkles } from "lucide-react";
import { Topbar } from "@/components/Topbar";
import { Card } from "@/components/ui";
import { api, friendlyError } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

const SUGGESTIONS = [
  "Which scooters need servicing?",
  "Show low battery vehicles",
  "Generate fleet summary",
  "Predict maintenance for the fleet",
  "Who are the worst performing riders?",
  "Generate weekly report",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm the EV Fleet Intelligence assistant, backed by a 10-agent LangGraph system. Ask me about vehicles, battery health, maintenance, deliveries, or riders.",
      agent: "Manager Agent",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text: string) {
    if (!text.trim() || sending) return;
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    try {
      const resp = await api.post("/api/chat", { message: text });
      setMessages((prev) => [...prev, { role: "assistant", content: resp.data.reply, agent: resp.data.agent }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "assistant", content: friendlyError(err), agent: "System" }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <Topbar title="AI Assistant" />
      <main className="p-4 lg:p-8 flex flex-col h-[calc(100vh-4rem)]">
        <Card className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                {m.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-950 flex items-center justify-center shrink-0">
                    <Bot size={16} className="text-brand-600 dark:text-brand-400" />
                  </div>
                )}
                <div className={`max-w-[75%] ${m.role === "user" ? "order-first" : ""}`}>
                  {m.role === "assistant" && m.agent && (
                    <p className="text-xs text-slate-400 mb-1 flex items-center gap-1">
                      <Sparkles size={11} /> {m.agent}
                    </p>
                  )}
                  <div
                    className={`px-4 py-2.5 rounded-2xl text-sm whitespace-pre-wrap ${
                      m.role === "user"
                        ? "bg-brand-600 text-white rounded-tr-sm"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-sm"
                    }`}
                  >
                    {m.content}
                  </div>
                </div>
                {m.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center shrink-0">
                    <UserIcon size={16} className="text-slate-500" />
                  </div>
                )}
              </div>
            ))}
            {sending && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-950 flex items-center justify-center shrink-0">
                  <Bot size={16} className="text-brand-600 dark:text-brand-400" />
                </div>
                <div className="px-4 py-2.5 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center gap-2">
                  <Loader2 size={14} className="animate-spin text-slate-500" />
                  <span className="text-sm text-slate-500">Routing to the right agent...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {messages.length <= 1 && (
            <div className="px-5 pb-3 flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="text-xs px-3 py-1.5 rounded-full border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage(input);
            }}
            className="border-t border-slate-200 dark:border-slate-800 p-4 flex gap-2"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about vehicles, battery, maintenance, riders..."
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="w-11 h-11 rounded-xl bg-brand-600 hover:bg-brand-700 text-white flex items-center justify-center disabled:opacity-50 shrink-0"
            >
              <Send size={18} />
            </button>
          </form>
        </Card>
      </main>
    </>
  );
}
