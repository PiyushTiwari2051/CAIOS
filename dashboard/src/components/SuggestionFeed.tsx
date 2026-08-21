"use client";

import React, { useState } from "react";
import { ActionPayload, ActionType } from "../lib/types";
import {
  ExternalLink,
  AppWindow,
  FileText,
  Clock,
  Play,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";

interface SuggestionFeedProps {
  suggestions: ActionPayload[];
  reasoning?: string;
  source: string;
  onExecute: (action: ActionPayload) => Promise<any>;
  isLoading: boolean;
  killSwitchActive: boolean;
}

const ACTION_BRUTAL_META: Record<
  ActionType,
  { label: string; icon: React.ReactNode; badgeBg: string }
> = {
  OPEN_APP: {
    label: "DESKTOP APP",
    icon: <AppWindow className="w-3.5 h-3.5 stroke-[2.5]" />,
    badgeBg: "bg-[#BAE6FD] text-black", // Sky Blue
  },
  OPEN_URL: {
    label: "WEB LINK",
    icon: <ExternalLink className="w-3.5 h-3.5 stroke-[2.5]" />,
    badgeBg: "bg-[#E9D5FF] text-black", // Lavender
  },
  CREATE_NOTE: {
    label: "SANDBOX NOTE",
    icon: <FileText className="w-3.5 h-3.5 stroke-[2.5]" />,
    badgeBg: "bg-[#BBF7D0] text-black", // Mint
  },
  SET_REMINDER: {
    label: "FOCUS TIMER",
    icon: <Clock className="w-3.5 h-3.5 stroke-[2.5]" />,
    badgeBg: "bg-[#FEF08A] text-black", // Yellow
  },
};

export const SuggestionFeed: React.FC<SuggestionFeedProps> = ({
  suggestions,
  reasoning,
  source,
  onExecute,
  isLoading,
  killSwitchActive,
}) => {
  const [executingIdx, setExecutingIdx] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<{ [key: number]: { success: boolean; msg: string } }>({});

  const handleExecute = async (action: ActionPayload, idx: number) => {
    setExecutingIdx(idx);
    try {
      // Directly open URL in browser tab on client click
      if (action.action_type === "OPEN_URL" && action.params?.url) {
        window.open(action.params.url, "_blank", "noopener,noreferrer");
      }
      
      const res = await onExecute(action);
      setFeedback((prev) => ({
        ...prev,
        [idx]: { success: res.success, msg: res.message },
      }));
    } catch (err: any) {
      setFeedback((prev) => ({
        ...prev,
        [idx]: { success: false, msg: err.message || "Execution error" },
      }));
    } finally {
      setExecutingIdx(null);
    }
  };

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-black tracking-wide text-black uppercase">
            Suggested Actions Matrix
          </h2>
          {reasoning && <p className="text-xs font-semibold text-neutral-600 mt-0.5">{reasoning}</p>}
        </div>

        <div className="neo-badge bg-[#BBF7D0] text-black text-[10px] px-2 py-0.5 font-mono font-black">
          STRICT ALLOW-LIST
        </div>
      </div>

      {/* Grid of Action Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 py-6">
          {[1, 2].map((i) => (
            <div
              key={i}
              className="h-28 rounded-xl neo-card animate-pulse flex items-center justify-center bg-white"
            >
              <Loader2 className="w-6 h-6 text-black animate-spin" />
            </div>
          ))}
        </div>
      ) : suggestions.length === 0 ? (
        <div className="p-8 text-center neo-card text-neutral-500 text-xs font-bold font-mono bg-white">
          NO ACTIONS AVAILABLE FOR THIS MODE
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {suggestions.map((action, idx) => {
            const meta = ACTION_BRUTAL_META[action.action_type] || ACTION_BRUTAL_META.OPEN_APP;
            const isExecuting = executingIdx === idx;
            const res = feedback[idx];

            return (
              <div
                key={idx}
                className="neo-card neo-card-interactive p-4 flex flex-col justify-between space-y-3 bg-white"
              >
                <div className="space-y-2">
                  {/* Badge + Param Tag */}
                  <div className="flex items-center justify-between">
                    <span
                      className={`neo-badge ${meta.badgeBg} text-[10px] px-2 py-0.5 flex items-center space-x-1 font-mono font-bold`}
                    >
                      {meta.icon}
                      <span>{meta.label}</span>
                    </span>

                    <span className="text-[11px] font-mono font-bold text-neutral-600 max-w-[140px] truncate bg-neutral-100 px-1.5 py-0.5 rounded border border-black">
                      {action.params?.app ||
                        action.params?.url ||
                        action.params?.filename ||
                        (action.params?.seconds ? `${action.params.seconds}s` : "")}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <div>
                    <h3 className="text-sm font-black text-black">
                      {action.title}
                    </h3>
                    <p className="text-xs font-medium text-neutral-700 mt-0.5 line-clamp-2 leading-relaxed">
                      {action.description}
                    </p>
                  </div>
                </div>

                {/* Bottom Bar: Status + Execute Button */}
                <div className="pt-2.5 border-t-2 border-black flex items-center justify-between">
                  <div className="text-xs font-mono font-bold">
                    {res ? (
                      <span
                        className={`inline-flex items-center space-x-1 ${
                          res.success ? "text-emerald-700 font-black" : "text-rose-700 font-black"
                        }`}
                      >
                        {res.success ? <CheckCircle className="w-3.5 h-3.5 stroke-[2.5]" /> : <AlertCircle className="w-3.5 h-3.5 stroke-[2.5]" />}
                        <span className="truncate max-w-[130px]">{res.msg}</span>
                      </span>
                    ) : (
                      <span className="text-neutral-400 text-[11px]">READY</span>
                    )}
                  </div>

                  <button
                    onClick={() => handleExecute(action, idx)}
                    disabled={isExecuting || killSwitchActive}
                    className={`neo-btn px-3.5 py-1.5 text-xs font-black uppercase tracking-wider ${
                      killSwitchActive
                        ? "bg-neutral-200 text-neutral-400 cursor-not-allowed shadow-none"
                        : "neo-btn-cyan"
                    }`}
                  >
                    {isExecuting ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin mr-1" />
                    ) : (
                      <Play className="w-3 h-3 fill-current mr-1 stroke-[2.5]" />
                    )}
                    <span>EXECUTE</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
