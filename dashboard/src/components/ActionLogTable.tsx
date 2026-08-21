"use client";

import React, { useState } from "react";
import { ActionLogEntry } from "../lib/types";
import { ListFilter, ShieldCheck, ChevronDown, ChevronRight, FileCheck, CheckCircle2, AlertOctagon } from "lucide-react";

interface ActionLogTableProps {
  logs: ActionLogEntry[];
  onRefresh: () => void;
  isLoading: boolean;
}

export const ActionLogTable: React.FC<ActionLogTableProps> = ({ logs }) => {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  const toggleExpand = (idx: number) => {
    setExpandedIdx(expandedIdx === idx ? null : idx);
  };

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
            const isExpanded = expandedIdx === idx;

            return (
              <div
                key={idx}
                onClick={() => toggleExpand(idx)}
                className="p-2.5 rounded-lg bg-[#FAF8F5] border-2 border-black shadow-[2px_2px_0px_0px_#000] text-xs transition-all cursor-pointer hover:bg-neutral-50"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 min-w-0 pr-2">
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

                  <div className="flex items-center space-x-2 shrink-0">
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
                    {isExpanded ? (
                      <ChevronDown className="w-3.5 h-3.5 text-black" />
                    ) : (
                      <ChevronRight className="w-3.5 h-3.5 text-neutral-400" />
                    )}
                  </div>
                </div>

                {/* Expanded Execution Proof Details */}
                {isExpanded && (
                  <div className="mt-2.5 pt-2 border-t border-dashed border-neutral-300 font-mono text-[11px] space-y-1.5 animate-fadeIn">
                    <div className="flex items-center justify-between text-neutral-600">
                      <span>Action Type: <strong className="text-black">{entry.action_type}</strong></span>
                      <span className="text-[10px] bg-white px-1.5 py-0.5 rounded border border-black text-black font-bold">
                        {isExecuted ? "✓ VERIFIED ON DISK" : isBlocked ? "✗ BLOCKED BY INTERLOCK" : "LOGGED"}
                      </span>
                    </div>

                    {entry.details && (
                      <div className="p-1.5 rounded bg-white border border-neutral-300 text-neutral-800">
                        <span className="text-[10px] text-neutral-400 uppercase block font-bold">Execution Result:</span>
                        {entry.details}
                      </div>
                    )}

                    {entry.params && Object.keys(entry.params).length > 0 && (
                      <div className="p-1.5 rounded bg-neutral-100 border border-neutral-300 text-[10px] text-neutral-700 overflow-x-auto">
                        <span className="text-[9px] text-neutral-500 uppercase block font-bold">Payload Parameters:</span>
                        {JSON.stringify(entry.params)}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="pt-2.5 mt-2 border-t-2 border-black flex items-center justify-between text-[11px] font-mono font-bold text-neutral-600">
        <span className="flex items-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5 text-black stroke-[2.5]" />
          <span>CLICK ANY ROW FOR VERIFIED DISK PROOF</span>
        </span>
        <span className="bg-neutral-100 px-1.5 py-0.5 rounded border border-black">SQLITE + LOG FILE</span>
      </div>
    </div>
  );
};
