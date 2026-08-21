"use client";

import React from "react";
import { Cpu, ShieldCheck } from "lucide-react";

interface SystemCardProps {
  modelProvider: string;
}

export const SystemCard: React.FC<SystemCardProps> = ({ modelProvider }) => {
  return (
    <div className="neo-card p-4 space-y-3 bg-white">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b-2 border-black">
        <div className="flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-black stroke-[2.5]" />
          <h2 className="text-xs font-black text-black uppercase tracking-wider">
            Container Isolation Quotas
          </h2>
        </div>
        <span className="neo-badge bg-[#BBF7D0] text-black text-[10px] px-2 py-0.5 font-mono font-black">
          HARD ENFORCED
        </span>
      </div>

      {/* Quota Grid */}
      <div className="grid grid-cols-2 gap-2 text-xs font-mono">
        <div className="p-2.5 rounded-lg bg-[#FAF8F5] border-2 border-black shadow-[2px_2px_0px_0px_#000]">
          <span className="text-[10px] font-black text-neutral-500 block uppercase">RAM QUOTA</span>
          <span className="font-black text-black">1024 MB (1 GB)</span>
        </div>

        <div className="p-2.5 rounded-lg bg-[#FAF8F5] border-2 border-black shadow-[2px_2px_0px_0px_#000]">
          <span className="text-[10px] font-black text-neutral-500 block uppercase">CPU LIMIT</span>
          <span className="font-black text-black">1.0 Core (Cap)</span>
        </div>

        <div className="p-2.5 rounded-lg bg-[#FAF8F5] border-2 border-black shadow-[2px_2px_0px_0px_#000]">
          <span className="text-[10px] font-black text-neutral-500 block uppercase">REASONING CORE</span>
          <span className="font-black text-black truncate block">Ollama (Local LLM)</span>
        </div>

        <div className="p-2.5 rounded-lg bg-[#FAF8F5] border-2 border-black shadow-[2px_2px_0px_0px_#000]">
          <span className="text-[10px] font-black text-neutral-500 block uppercase">MOUNT ISOLATION</span>
          <span className="font-black text-black">./sandbox Only</span>
        </div>
      </div>
    </div>
  );
};
