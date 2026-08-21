"use client";

import React from "react";
import { ShieldAlert, Power, Lock, BookOpen, GitBranch, LayoutDashboard } from "lucide-react";

interface HeaderProps {
  killSwitchActive: boolean;
  onToggleKillSwitch: () => void;
  isConnected: boolean;
  activeProcess: string;
  onOpenPitchModal: () => void;
  activeTab: "workspace" | "causal";
  onSelectTab: (tab: "workspace" | "causal") => void;
}

export const Header: React.FC<HeaderProps> = ({
  killSwitchActive,
  onToggleKillSwitch,
  isConnected,
  activeProcess,
  onOpenPitchModal,
  activeTab,
  onSelectTab,
}) => {
  return (
    <header className="border-b-[3px] border-black bg-white sticky top-0 z-50">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        
        {/* Left: Brandmark + View Switcher */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-10 h-10 rounded-lg bg-[#FEF08A] border-2 border-black shadow-[3px_3px_0px_0px_#000] flex items-center justify-center font-black text-xl text-black">
              C
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-black text-xl tracking-tight text-black">
                  CAIOS
                </span>
                <span className="neo-badge bg-[#E9D5FF] text-[10px] px-2 py-0.5 tracking-wider font-mono">
                  CAUSAL-ADAPTIVE OS
                </span>
              </div>
            </div>
          </div>

          {/* Studio Navigation Tabs */}
          <div className="hidden sm:flex items-center p-1 rounded-xl bg-[#FAF7F0] border-2 border-black shadow-[2px_2px_0px_0px_#000] gap-1">
            <button
              onClick={() => onSelectTab("workspace")}
              className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all flex items-center space-x-1.5 ${
                activeTab === "workspace"
                  ? "bg-black text-white shadow-none"
                  : "bg-transparent text-black hover:bg-neutral-100"
              }`}
            >
              <LayoutDashboard className="w-3.5 h-3.5 stroke-[2.5]" />
              <span>Workspace Shell</span>
            </button>

            <button
              onClick={() => onSelectTab("causal")}
              className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all flex items-center space-x-1.5 ${
                activeTab === "causal"
                  ? "bg-[#FEF08A] text-black shadow-none border border-black"
                  : "bg-transparent text-black hover:bg-neutral-100"
              }`}
            >
              <GitBranch className="w-3.5 h-3.5 stroke-[2.5]" />
              <span>Causal Decision Studio</span>
            </button>
          </div>
        </div>

        {/* Center: Live Context Telemetry Stamp */}
        <div className="hidden lg:flex items-center space-x-2.5 px-3.5 py-1.5 rounded-lg bg-[#FAF8F5] border-2 border-black shadow-[2px_2px_0px_0px_#000] text-xs font-mono font-bold text-black">
          <span className={`w-2.5 h-2.5 rounded-full border border-black ${isConnected ? "bg-[#4ADE80]" : "bg-[#FBBF24] animate-pulse"}`} />
          <span className="text-neutral-500 uppercase">ACTIVE CONTEXT:</span>
          <span className="text-black bg-[#FEF08A] px-2 py-0.5 rounded border border-black font-black">
            {activeProcess ? activeProcess : "ambient / desktop"}
          </span>
          <span className="text-[10px] text-neutral-400 font-normal">3.0s SENSOR</span>
        </div>

        {/* Right Controls: Pitch Brief + Safety Stamp + Kill Switch */}
        <div className="flex items-center space-x-2.5">
          {/* Research Brief Button for Judges */}
          <button
            onClick={onOpenPitchModal}
            className="neo-btn neo-btn-lavender px-3 py-1.5 text-xs uppercase tracking-wider flex items-center space-x-1.5"
            title="Open Competitive Analysis & Research Brief for Judges"
          >
            <BookOpen className="w-3.5 h-3.5 stroke-[2.5]" />
            <span className="hidden sm:inline">PITCH & SPECS</span>
          </button>

          {/* Safety Allow-List Stamp */}
          <div className="hidden xl:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#BBF7D0] border-2 border-black shadow-[2px_2px_0px_0px_#000] text-xs font-black text-black">
            <Lock className="w-3.5 h-3.5 stroke-[2.5]" />
            <span>ALLOW-LIST SAFE</span>
          </div>

          {/* Master Kill Switch Button */}
          <button
            onClick={onToggleKillSwitch}
            className={`neo-btn px-4 py-2 text-xs uppercase tracking-wider ${
              killSwitchActive
                ? "bg-[#EF4444] text-white shadow-[4px_4px_0px_0px_#000] animate-pulse"
                : "neo-btn-rose"
            }`}
            title="Master Hardware Emergency Interlock"
          >
            {killSwitchActive ? (
              <span className="flex items-center space-x-1.5 font-black text-white">
                <ShieldAlert className="w-4 h-4 stroke-[2.5]" />
                <span>INTERLOCK ENGAGED</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1.5 text-black">
                <Power className="w-4 h-4 text-black stroke-[2.5]" />
                <span>KILL SWITCH: ARMED</span>
              </span>
            )}
          </button>
        </div>

      </div>
    </header>
  );
};
