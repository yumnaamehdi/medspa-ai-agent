"use client";

import { FormEvent, useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your AI aesthetics assistant. Ask me about treatments, pricing, or clinic policies.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage(event: FormEvent) {
    event.preventDefault();

    const question = input.trim();

    if (!question || loading) return;

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: question,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: question,
        }),
      });

      if (!response.ok) {
        throw new Error("Request failed");
      }

      const data = await response.json();

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.response,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "I couldn't connect to the AI assistant. Please make sure the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const suggestions = [
    "How much is lip filler?",
    "What does chin filler do?",
    "How much is Botox?",
    "What is your cancellation policy?",
  ];

  return (
    <main className="min-h-screen bg-[#faf7f8] text-[#2b2427]">
      <nav className="flex items-center justify-between border-b border-[#eadfe3] bg-white px-8 py-5">
        <div>
          <p className="text-lg font-semibold tracking-[0.18em]">
            AESTHETIC AI
          </p>
          <p className="text-xs text-[#9b858e]">
            Intelligent aesthetics concierge
          </p>
        </div>

        <div className="rounded-full bg-[#f7e9ee] px-4 py-2 text-xs font-medium text-[#8b596b]">
          AI Powered
        </div>
      </nav>

      <section className="mx-auto grid min-h-[calc(100vh-89px)] max-w-7xl gap-10 px-6 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:px-10">
        <div className="flex flex-col justify-center">
          <div className="mb-5 w-fit rounded-full border border-[#e8d4dc] bg-white px-4 py-2 text-xs tracking-wider text-[#966578]">
            YOUR PERSONAL AESTHETICS CONCIERGE
          </div>

          <h1 className="max-w-xl text-5xl font-medium leading-[1.08] tracking-tight md:text-6xl">
            Beauty questions,
            <span className="block font-serif italic text-[#bd8298]">
              intelligently answered.
            </span>
          </h1>

          <p className="mt-6 max-w-lg text-base leading-7 text-[#786a70]">
            Explore treatments, pricing, and clinic information through an
            AI-powered assistant grounded in verified clinic knowledge.
          </p>

          <div className="mt-10">
            <p className="mb-4 text-xs font-semibold tracking-[0.15em] text-[#9b858e]">
              TRY ASKING
            </p>

            <div className="flex max-w-xl flex-wrap gap-3">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="rounded-full border border-[#e5d6dc] bg-white px-4 py-2.5 text-sm text-[#695b61] shadow-sm transition hover:border-[#cfa7b6] hover:bg-[#fffafb]"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>

          <p className="mt-10 max-w-lg text-xs leading-5 text-[#a09197]">
            This AI provides general clinic information and does not replace
            consultation or medical assessment by a licensed provider.
          </p>
        </div>

        <div className="flex items-center justify-center">
          <div className="flex h-[650px] w-full max-w-xl flex-col overflow-hidden rounded-[32px] border border-[#eadfe3] bg-white shadow-[0_30px_80px_rgba(89,61,72,0.12)]">
            <div className="flex items-center gap-3 border-b border-[#eee4e8] px-6 py-5">
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#f5e4ea] text-lg">
                ✦
              </div>

              <div>
                <p className="font-medium">Aesthetics Assistant</p>
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                  <span className="text-xs text-[#96868c]">Online</span>
                </div>
              </div>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto bg-[#fffdfd] p-6">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user"
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[82%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                      message.role === "user"
                        ? "rounded-br-md bg-[#2f272a] text-white"
                        : "rounded-bl-md bg-[#f6ecef] text-[#51464a]"
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-2xl rounded-bl-md bg-[#f6ecef] px-5 py-3 text-sm text-[#8b737c]">
                    Thinking...
                  </div>
                </div>
              )}
            </div>

            <form
              onSubmit={sendMessage}
              className="border-t border-[#eee4e8] bg-white p-5"
            >
              <div className="flex items-center gap-3 rounded-2xl border border-[#e5d8dd] bg-[#fcf9fa] p-2 pl-4 focus-within:border-[#cda4b3]">
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="Ask about treatments, pricing..."
                  className="flex-1 bg-transparent text-sm outline-none placeholder:text-[#aa9ca1]"
                />

                <button
                  type="submit"
                  disabled={loading}
                  className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#2f272a] text-lg text-white transition hover:bg-[#493b40] disabled:opacity-50"
                >
                  ↑
                </button>
              </div>

              <p className="mt-3 text-center text-[10px] text-[#aaa0a4]">
                AI-generated information • Medical eligibility requires provider
                assessment
              </p>
            </form>
          </div>
        </div>
      </section>
    </main>
  );
}