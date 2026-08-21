"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Header } from "../components/Header";
import { ModeBanner } from "../components/ModeBanner";
import { SuggestionFeed } from "../components/SuggestionFeed";
import { IntentInput } from "../components/IntentInput";
import { ActionLogTable } from "../components/ActionLogTable";
import { SystemCard } from "../components/SystemCard";
import { CausalStudio } from "../components/CausalStudio";
import { PitchModal } from "../components/PitchModal";
import {
  fetchCurrentContext,
  fetchSuggestions,
  executeAction,
  fetchActionLogs,
  toggleKillSwitch,
  setModeOverride,
} from "../lib/api";
import {
  ContextState,
  ActionPayload,
  ActionLogEntry,
  ModeType,
} from "../lib/types";
import { ShieldAlert, Loader2 } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"workspace" | "causal">("workspace");
  const [contextState, setContextState] = useState<ContextState | null>(null);
  const [suggestions, setSuggestions] = useState<ActionPayload[]>([]);
  const [suggestionSource, setSuggestionSource] = useState<string>("rule_fallback");
  const [suggestionReasoning, setSuggestionReasoning] = useState<string>("");
  const [logs, setLogs] = useState<ActionLogEntry[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState<boolean>(false);
  const [isPitchModalOpen, setIsPitchModalOpen] = useState<boolean>(false);

  // Sync state with Orchestrator every 2.5 seconds
  const loadState = useCallback(async () => {
    try {
      const state = await fetchCurrentContext();
      setContextState(state);
      setIsConnected(true);
    } catch (err) {
      setIsConnected(false);
    }

    try {
      const actionLogs = await fetchActionLogs(25);
      setLogs(actionLogs);
    } catch (err) {
      // Offline fallback
    }
  }, []);

  // Fetch suggestions when mode shifts
  const loadSuggestionsForMode = useCallback(
    async (mode: ModeType, prompt?: string) => {
      setIsLoadingSuggestions(true);
      try {
        const resp = await fetchSuggestions(
          mode,
          prompt,
          contextState?.current_context?.window_title,
          contextState?.current_context?.process_name
        );
        setSuggestions(resp.suggestions || []);
        setSuggestionSource(resp.source || "rule_fallback");
        setSuggestionReasoning(resp.reasoning || "");
      } catch (err) {
        console.error("Failed to load suggestions:", err);
      } finally {
        setIsLoadingSuggestions(false);
      }
    },
    [contextState?.current_context?.window_title, contextState?.current_context?.process_name]
  );

  // Initial mount polling
  useEffect(() => {
    loadState();
    const interval = setInterval(loadState, 2500);
    return () => clearInterval(interval);
  }, [loadState]);

  // Sync suggestions whenever mode changes
  useEffect(() => {
    if (contextState?.current_mode?.mode) {
      loadSuggestionsForMode(contextState.current_mode.mode);
    }
  }, [contextState?.current_mode?.mode, loadSuggestionsForMode]);

  // Keyboard shortcut listeners
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (["input", "textarea"].includes((e.target as HTMLElement).tagName.toLowerCase())) return;
      if (e.key === "1") handleSetOverride("CODING");
      else if (e.key === "2") handleSetOverride("WRITING");
      else if (e.key === "3") handleSetOverride("STUDYING");
      else if (e.key === "4") handleSetOverride("MEETING");
      else if (e.key === "5") handleSetOverride("IDLE");
      else if (e.key === "0" || e.key === "Escape") handleSetOverride(null);
      else if (e.key.toLowerCase() === "c") setActiveTab((prev) => (prev === "workspace" ? "causal" : "workspace"));
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Handlers
  const handleToggleKillSwitch = async () => {
    try {
      const res = await toggleKillSwitch();
      if (contextState) {
        setContextState({ ...contextState, kill_switch_active: res.is_active });
      }
      loadState();
    } catch (err) {
      console.error("Kill switch error:", err);
    }
  };

  const handleSetOverride = async (mode: ModeType | null) => {
    try {
      await setModeOverride(mode);
      await loadState();
      if (mode) {
        loadSuggestionsForMode(mode);
      }
    } catch (err) {
      console.error("Mode override error:", err);
    }
  };

  const handleExecute = async (action: ActionPayload) => {
    const result = await executeAction(action);
    const newLogs = await fetchActionLogs(25);
    setLogs(newLogs);
    return result;
  };

  const handleIntentPrompt = async (prompt: string) => {
    const activeMode = contextState?.current_mode?.mode || "IDLE";
    await loadSuggestionsForMode(activeMode, prompt);
  };

  const isKillSwitchActive = contextState?.kill_switch_active || false;

  return (
    <div className="min-h-screen dot-paper-bg text-black flex flex-col justify-between">
      
      {/* Header with Studio Switcher Tabs */}
      <Header
        killSwitchActive={isKillSwitchActive}
        onToggleKillSwitch={handleToggleKillSwitch}
        isConnected={isConnected}
        activeProcess={contextState?.current_context?.process_name || ""}
        onOpenPitchModal={() => setIsPitchModalOpen(true)}
        activeTab={activeTab}
        onSelectTab={setActiveTab}
      />

      {/* Emergency Lockdown Notice with Hazard Stripes */}
      {isKillSwitchActive && (
        <div className="hazard-stripes-light text-white px-4 py-2 border-b-[3px] border-black text-xs font-black uppercase tracking-widest flex items-center justify-center space-x-2 shadow-md">
          <ShieldAlert className="w-4 h-4 stroke-[3]" />
          <span>CAIOS SAFETY INTERLOCK ACTIVE — ALL ACTIONS ARE CURRENTLY HALTED</span>
        </div>
      )}

      {/* Main Viewport */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 sm:px-6 py-5 flex flex-col justify-center">
        
        {activeTab === "causal" ? (
          /* Causal Intelligence Studio View */
          <CausalStudio />
        ) : (
          /* Adaptive Workspace Shell View */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            
            {/* Left Column: Primary Adaptive Studio (7 of 12 cols) */}
            <div className="lg:col-span-7 space-y-4">
              {/* 1. Mode Banner */}
              {contextState?.current_mode ? (
                <ModeBanner
                  classification={contextState.current_mode}
                  manualOverride={contextState.manual_override}
                  onSetOverride={handleSetOverride}
                  windowTitle={contextState.current_context.window_title}
                />
              ) : (
                <div className="h-32 rounded-2xl neo-card animate-pulse flex items-center justify-center text-neutral-400 font-mono text-xs font-bold bg-white">
                  <Loader2 className="w-4 h-4 mr-2 animate-spin text-black" />
                  CONNECTING TO CAIOS ORCHESTRATOR...
                </div>
              )}

              {/* 2. Natural Intent Input */}
              <IntentInput onSubmit={handleIntentPrompt} isLoading={isLoadingSuggestions} />

              {/* 3. Action Cards Grid */}
              <SuggestionFeed
                suggestions={suggestions}
                reasoning={suggestionReasoning}
                source={suggestionSource}
                onExecute={handleExecute}
                isLoading={isLoadingSuggestions}
                killSwitchActive={isKillSwitchActive}
              />
            </div>

            {/* Right Column: Quotas & Activity Ledger (5 of 12 cols) */}
            <div className="lg:col-span-5 space-y-4 flex flex-col">
              {/* 4. Hardware Quotas Card */}
              <SystemCard modelProvider="Ollama (Local)" />

              {/* 5. Activity & Audit Log */}
              <div className="flex-1">
                <ActionLogTable logs={logs} onRefresh={loadState} isLoading={false} />
              </div>
            </div>

          </div>
        )}

      </main>

      {/* Neo-Brutalist Footer */}
      <footer className="border-t-[3px] border-black bg-[#F4F0E8] py-2.5 px-6 flex items-center justify-between text-xs font-mono font-bold text-black">
        <span>CAIOS • Causal-Adaptive Intelligence Operating System</span>
        <span className="hidden sm:inline">SHORTCUTS: [1-5] Modes • [C] Toggle Causal Studio • [0/Esc] Auto Sensor</span>
        <span>DOWHY CAUSAL PIPELINE • NEO4J GRAPH DB READY</span>
      </footer>

      {/* Interactive Pitch & Research Brief Modal */}
      <PitchModal isOpen={isPitchModalOpen} onClose={() => setIsPitchModalOpen(false)} />

    </div>
  );
}
