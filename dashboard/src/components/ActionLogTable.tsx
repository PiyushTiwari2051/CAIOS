"use client";

import React from "react";
import { ActionLogEntry } from "../lib/types";
import { ListFilter, ShieldCheck } from "lucide-react";

interface ActionLogTableProps {
  logs: ActionLogEntry[];
  onRefresh: () => void;
  isLoading: boolean;
}

export const ActionLogTable: React.FC<ActionLogTableProps> = ({ logs }) => {
  return (
    <div className="neo-card p-4 flex flex-col h-full bg-white">
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b-2 border-black">
        <div className="flex items-center space-x-2">
          <ListFilter className="w-4 h-4 text-black stroke-[2.5]" />
          <h2 className="text-xs font-black text-black uppercase tracking-wider">
            Audit Ledger (actions.log)
          </h2>
        </div>

        <span className="text-[11px] font-mono font-bold text-black bg-neutral-100 px-2 py-0.5 rounded border border-black">
          {logs.length} RECORDS
        </span>
      </div>

      {/* Activity List */}
      <div className="flex-1 overflow-y-auto space-y-2 pt-3 max-h-[360px] pr-1">
        {logs.length === 0 ? (
          <div className="py-12 text-center text-neutral-400 font-mono font-bold text-xs">
            AWAITING ACTION TELEMETRY...
          </div>
        ) : (
          logs.map((entry, idx) => {
            const isExecuted = entry.status === "EXECUTED";
            const isBlocked = entry.status === "BLOCKED_BY_KILLSWITCH";
            const isFailed = entry.status === "FAILED";

            return (
              <div
                key={idx}
                className="p-2.5 rounded-lg bg-[#FAF8F5] border-2 border-black shadow-[2px_2px_0px_0px_#000] flex items-center justify-between text-xs transition-transform hover:-translate-y-0.5"
              >
                <div className="flex items-center space-x-2.5 min-w-0 pr-2">
                  {/* Status Indicator Stamp */}
                  <span
                    className={`w-2.5 h-2.5 rounded-full border border-black shrink-0 ${
                      isExecuted
                        ? "bg-[#4ADE80]"
                        : isBlocked
                        ? "bg-[#EF4444]"
                        : isFailed
                        ? "bg-[#F59E0B]"
                        : "bg-[#38BDF8]"
                    }`}
                  />

                  <span className="text-[10px] text-neutral-500 font-mono font-bold shrink-0">
                    {entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "--:--"}
                  </span>

                  <span className="font-bold text-black truncate text-xs">
                    {entry.title}
                  </span>
                </div>

                <div className="shrink-0">
                  <span
                    className={`neo-badge text-[9px] px-2 py-0.5 font-mono ${
                      isExecuted
                        ? "bg-[#BBF7D0] text-black"
                        : isBlocked
                        ? "bg-[#FECDD3] text-black"
                        : isFailed
                        ? "bg-[#FED7AA] text-black"
                        : "bg-[#BAE6FD] text-black"
                    }`}
                  >
                    {isExecuted ? "EXECUTED" : isBlocked ? "HALTED" : entry.status}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="pt-2.5 mt-2 border-t-2 border-black flex items-center justify-between text-[11px] font-mono font-bold text-neutral-600">
        <span className="flex items-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5 text-black stroke-[2.5]" />
          <span>SYNCHRONOUS PRE-EXECUTION LOGGING</span>
        </span>
        <span className="bg-neutral-100 px-1.5 py-0.5 rounded border border-black">SQLITE + LOG FILE</span>
      </div>
    </div>
  );
};
