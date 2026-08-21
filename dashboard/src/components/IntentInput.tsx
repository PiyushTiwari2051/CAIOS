"use client";

import React, { useState } from "react";
import { ArrowRight, Loader2 } from "lucide-react";

interface IntentInputProps {
  onSubmit: (prompt: string) => Promise<void>;
  isLoading: boolean;
}

export const IntentInput: React.FC<IntentInputProps> = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    await onSubmit(prompt.trim());
    setPrompt("");
  };

  const handleChip = (text: string) => {
    setPrompt(text);
    onSubmit(text);
  };

  return (
    <div className="neo-card p-4 space-y-3 bg-white">
      <form onSubmit={handleSubmit} className="relative flex items-center gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type a workspace intent (e.g. 'Setup research workspace for AI agents' or 'Open coding scratchpad')..."
            className="w-full pl-4 pr-10 py-2.5 bg-white border-2 border-black rounded-lg text-xs sm:text-sm font-bold text-black placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-black shadow-[2px_2px_0px_0px_#000]"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !prompt.trim()}
          className="neo-btn neo-btn-yellow px-5 py-2.5 text-xs font-black shrink-0 disabled:opacity-40"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <span>ADAPT</span>
              <ArrowRight className="w-4 h-4 ml-1 stroke-[2.5]" />
            </>
          )}
        </button>
      </form>

      {/* Suggested Quick Stamp Chips */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-[11px] font-mono font-black text-neutral-500 uppercase mr-1">
          SUGGESTIONS:
        </span>
        {[
          { text: "Prepare literature review", color: "bg-[#FEF08A]" },
          { text: "Setup coding flow & terminal", color: "bg-[#BBF7D0]" },
          { text: "Start 25m focus sprint", color: "bg-[#FED7AA]" },
          { text: "Create meeting action notes", color: "bg-[#FECDD3]" },
        ].map((chip, i) => (
          <button
            key={i}
            type="button"
            onClick={() => handleChip(chip.text)}
            className={`neo-badge ${chip.color} text-black text-xs px-2.5 py-1 transition-all hover:-translate-y-0.5 hover:shadow-[3px_3px_0px_0px_#000] active:translate-y-0.5`}
          >
            {chip.text}
          </button>
        ))}
      </div>
    </div>
  );
};
