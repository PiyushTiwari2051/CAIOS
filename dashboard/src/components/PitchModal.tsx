"use client";

import React from "react";
import { X, ShieldCheck, Cpu, Terminal, Zap, Check, AlertTriangle } from "lucide-react";

interface PitchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PitchModal: React.FC<PitchModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto dark-neo-box bg-[#11141d] border-2 border-[#3d455b] p-6 space-y-6 text-white shadow-[8px_8px_0px_0px_#000]">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b-2 border-[#2b3040]">
          <div>
            <div className="flex items-center space-x-2">
              <span className="dark-neo-badge bg-[#FEF08A] text-black text-xs px-2.5 py-0.5 font-mono font-black">
                RESEARCH BRIEF & SPECS
              </span>
              <h2 className="text-xl font-black tracking-tight text-white">
                CAIOS Architecture & Competitive Wedge
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Prepared for hackathon judges — Local-first adaptive workspace shell
            </p>
          </div>

          <button
            onClick={onClose}
            className="dark-neo-btn dark-neo-btn-yellow p-1.5 rounded-lg text-black"
          >
            <X className="w-5 h-5 stroke-[2.5]" />
          </button>
        </div>

        {/* Section 1: The Problem */}
        <div className="space-y-2">
          <h3 className="text-sm font-black text-[#FEF08A] uppercase tracking-wider">
            1. The Problem: Fragmented Workflows & Static Desktops
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Knowledge workers juggle 10+ disjointed apps with zero shared context. Traditional OS taskbars remain completely static regardless of mode (coding, writing, researching, meetings). Pre-programmed automation (Shortcuts, Zapier) requires manual rule configuration and cannot infer ambient intent.
          </p>
        </div>

        {/* Section 2: Competitive Positioning Matrix */}
        <div className="space-y-2">
          <h3 className="text-sm font-black text-[#A7F3D0] uppercase tracking-wider">
            2. Defensible Wedge vs Prior Art
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse font-mono">
              <thead>
                <tr className="bg-[#1a1e2b] border border-[#2b3040] text-slate-300 text-[11px]">
                  <th className="p-2.5">Approach</th>
                  <th className="p-2.5">Category</th>
                  <th className="p-2.5">Limitations</th>
                  <th className="p-2.5 text-[#FEF08A]">CAIOS Advantage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#2a2f3d] text-slate-300 text-[11px]">
                <tr className="bg-[#141722]">
                  <td className="p-2.5 font-bold text-white">AIOS (Rutgers)</td>
                  <td className="p-2.5">LLM Kernel</td>
                  <td className="p-2.5 text-slate-400">Dev framework, complex</td>
                  <td className="p-2.5 font-bold text-[#A7F3D0]">Consumer-facing shell layer</td>
                </tr>
                <tr className="bg-[#141722]">
                  <td className="p-2.5 font-bold text-white">UFO2 (Microsoft)</td>
                  <td className="p-2.5">Windows UI Agent</td>
                  <td className="p-2.5 text-slate-400">Heavyweight automation</td>
                  <td className="p-2.5 font-bold text-[#A7F3D0]">Lightweight allow-listed actions</td>
                </tr>
                <tr className="bg-[#141722]">
                  <td className="p-2.5 font-bold text-white">Copilot+ / Apple</td>
                  <td className="p-2.5">OS Native AI</td>
                  <td className="p-2.5 text-slate-400">Cloud-hybrid, vendor lock</td>
                  <td className="p-2.5 font-bold text-[#A7F3D0]">100% Local-first, OS-agnostic</td>
                </tr>
                <tr className="bg-[#141722]">
                  <td className="p-2.5 font-bold text-white">Rabbit R1 / Humane</td>
                  <td className="p-2.5">AI Hardware</td>
                  <td className="p-2.5 text-slate-400">Expensive new device</td>
                  <td className="p-2.5 font-bold text-[#A7F3D0]">Software on laptop you own</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Section 3: Hard Safety Architecture */}
        <div className="space-y-2">
          <h3 className="text-sm font-black text-[#FECDD3] uppercase tracking-wider">
            3. Laptop-Safe Architecture (Non-Negotiable Constraints)
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-[#141722] border border-[#2b3040]">
              <span className="font-bold text-[#FEF08A] block">Docker 1GB RAM / 1 CPU Cap</span>
              <span className="text-slate-400">Reasoning service runs unprivileged with single ./sandbox mount.</span>
            </div>
            <div className="p-3 rounded-lg bg-[#141722] border border-[#2b3040]">
              <span className="font-bold text-[#A7F3D0] block">Strict Enum Allow-List</span>
              <span className="text-slate-400">Only 4 actions permitted (Open App, URL, Note, Reminder). Zero raw shell execution.</span>
            </div>
            <div className="p-3 rounded-lg bg-[#141722] border border-[#2b3040]">
              <span className="font-bold text-[#BAE6FD] block">Synchronous Audit Log</span>
              <span className="text-slate-400">Every single action logged to actions.log and SQLite BEFORE execution.</span>
            </div>
            <div className="p-3 rounded-lg bg-[#141722] border border-[#2b3040]">
              <span className="font-bold text-[#FECDD3] block">Hardware Emergency Stop</span>
              <span className="text-slate-400">Dashboard Kill-Switch immediately blocks all execution with HTTP 423 Locked.</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-[#2b3040] flex items-center justify-between text-xs font-mono text-slate-500">
          <span>CAIOS • Casual Adaptive Intelligence Operating System</span>
          <button
            onClick={onClose}
            className="dark-neo-btn dark-neo-btn-mint px-4 py-1.5 text-xs font-black uppercase text-black"
          >
            CLOSE BRIEF
          </button>
        </div>

      </div>
    </div>
  );
};
