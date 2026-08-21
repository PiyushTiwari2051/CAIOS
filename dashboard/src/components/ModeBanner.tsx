"use client";

import React from "react";
import { ModeClassification, ModeType } from "../lib/types";
import { Code, PenTool, BookOpen, Users, Coffee, RefreshCw } from "lucide-react";

interface ModeBannerProps {
  classification: ModeClassification;
  manualOverride: ModeType | null;
  onSetOverride: (mode: ModeType | null) => void;
  windowTitle: string;
}

const NEO_LIGHT_MODES: Record<
  ModeType,
  {
    title: string;
    subtitle: string;
    bgCard: string;
    iconBg: string;
    icon: React.ReactNode;
  }
> = {
  CODING: {
    title: "Coding & Development Studio",
    subtitle: "Active IDE/Terminal detected. Dev scratchpads & terminal actions ready.",
    bgCard: "bg-[#BBF7D0]", // Mint
    iconBg: "bg-[#6EE7B7]",
    icon: <Code className="w-5 h-5 text-black stroke-[2.5]" />,
  },
  WRITING: {
    title: "Writing & Document Desk",
    subtitle: "Word processor/markdown active. Focus sprint timers & drafts loaded.",
    bgCard: "bg-[#E9D5FF]", // Lavender
    iconBg: "bg-[#C084FC]",
    icon: <PenTool className="w-5 h-5 text-black stroke-[2.5]" />,
  },
  STUDYING: {
    title: "Research & Literature Hub",
    subtitle: "Research materials active. Reference papers & notes templates available.",
    bgCard: "bg-[#FEF08A]", // Sun Yellow
    iconBg: "bg-[#FDE047]",
    icon: <BookOpen className="w-5 h-5 text-black stroke-[2.5]" />,
  },
  MEETING: {
    title: "Meeting & Live Collaboration",
    subtitle: "Communication app active. Action items & minutes recording armed.",
    bgCard: "bg-[#FECDD3]", // Rose
    iconBg: "bg-[#F43F5E]",
    icon: <Users className="w-5 h-5 text-black stroke-[2.5]" />,
  },
  IDLE: {
    title: "Ambient Equilibrium",
    subtitle: "System resting in passive monitoring. Quick launch tools available.",
    bgCard: "bg-[#BAE6FD]", // Sky Blue
    iconBg: "bg-[#38BDF8]",
    icon: <Coffee className="w-5 h-5 text-black stroke-[2.5]" />,
  },
};

const MODE_BUTTONS: { key: ModeType; label: string; num: string }[] = [
  { key: "CODING", label: "Code", num: "1" },
  { key: "WRITING", label: "Write", num: "2" },
  { key: "STUDYING", label: "Study", num: "3" },
  { key: "MEETING", label: "Meet", num: "4" },
  { key: "IDLE", label: "Idle", num: "5" },
];

export const ModeBanner: React.FC<ModeBannerProps> = ({
  classification,
  manualOverride,
  onSetOverride,
  windowTitle,
}) => {
  const currentMode = classification?.mode || "IDLE";
  const meta = NEO_LIGHT_MODES[currentMode] || NEO_LIGHT_MODES.IDLE;
  const confidence = Math.round((classification?.confidence || 0.95) * 100);

  return (
    <div className={`p-5 rounded-2xl border-[2.5px] border-black shadow-[4px_4px_0px_0px_#000] ${meta.bgCard} transition-colors duration-200`}>
      
      {/* Row 1: Mode Header & Title */}
      <div className="flex items-start space-x-3.5">
        <div className={`w-11 h-11 rounded-xl border-2 border-black shadow-[2px_2px_0px_0px_#000] ${meta.iconBg} flex items-center justify-center shrink-0`}>
          {meta.icon}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-xl font-black tracking-tight text-black">
              {meta.title}
            </h1>
            <span className="neo-badge bg-white text-black text-[11px] px-2 py-0.5 font-mono">
              {confidence}% CONF
            </span>
            {classification?.is_manual_override && (
              <span className="neo-badge bg-[#FED7AA] text-black text-[11px] px-2 py-0.5 font-mono">
                MANUAL OVERRIDE
              </span>
            )}
          </div>

          <p className="text-xs font-semibold text-neutral-800 mt-1 truncate">
            {windowTitle ? `Foreground: "${windowTitle}"` : meta.subtitle}
          </p>
        </div>
      </div>

      {/* Row 2: Inference Rationale + Mode Buttons Bar */}
      <div className="mt-4 pt-3.5 border-t-2 border-black flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        
        {/* Left: Context Inference Pill */}
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000] text-xs font-bold text-black max-w-full">
          <span className="text-[10px] font-mono uppercase text-neutral-500 shrink-0">INFERENCE:</span>
          <span className="truncate">{classification?.reasoning || "Context mapped to mode."}</span>
        </div>

        {/* Right: Mode Switcher Bar (Fully enclosed, will never overflow) */}
        <div className="flex flex-wrap items-center p-1 rounded-xl bg-white border-2 border-black shadow-[2px_2px_0px_0px_#000] gap-1 shrink-0">
          {/* Auto Sensor Button */}
          <button
            onClick={() => onSetOverride(null)}
            className={`px-2.5 py-1 rounded-lg text-xs font-black transition-all flex items-center space-x-1 ${
              manualOverride === null
                ? "bg-black text-white shadow-none"
                : "bg-transparent text-black hover:bg-neutral-100"
            }`}
            title="Return to automatic window detection"
          >
            <RefreshCw className="w-3 h-3 stroke-[2.5]" />
            <span>Auto</span>
          </button>

          {/* Mode Presets */}
          {MODE_BUTTONS.map((item) => {
            const isSelected = manualOverride === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onSetOverride(item.key)}
                className={`px-2.5 py-1 rounded-lg text-xs font-black transition-all flex items-center space-x-1 ${
                  isSelected
                    ? "bg-black text-white shadow-none"
                    : "bg-transparent text-black hover:bg-neutral-100"
                }`}
              >
                <span>{item.label}</span>
                <span className={`text-[10px] font-mono ${isSelected ? "text-neutral-300" : "text-neutral-400"}`}>
                  [{item.num}]
                </span>
              </button>
            );
          })}
        </div>

      </div>

    </div>
  );
};
