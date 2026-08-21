"use client";

import React, { useState, useEffect } from "react";
import {
  fetchCausalDomains,
  fetchCausalGraph,
  fetchCausalEstimate,
  simulateCounterfactual,
} from "../lib/api";
import {
  CausalDomain,
  CausalGraph,
  CausalNode,
  CausalEstimationResult,
  CounterfactualResult,
} from "../lib/types";
import {
  GitBranch,
  Sliders,
  ShieldCheck,
  ArrowRight,
  TrendingDown,
  TrendingUp,
  Database,
  Layers,
  HelpCircle,
  Play,
  Terminal,
  CheckCircle2,
  ExternalLink,
  Loader2,
  Info,
} from "lucide-react";

// Predefined Visual Layout Coordinates for 5-Node Causal Graphs (X, Y)
const NODE_COORDINATES: Record<string, { x: number; y: number }> = {
  // Developer Flow
  task_complexity: { x: 90, y: 150 },
  context_switching: { x: 260, y: 75 },
  cognitive_load: { x: 440, y: 150 },
  bug_rate: { x: 620, y: 70 },
  deep_work_time: { x: 620, y: 230 },

  // BFSI Risk
  transaction_risk: { x: 90, y: 150 },
  auth_friction: { x: 260, y: 75 },
  user_latency: { x: 440, y: 150 },
  fraud_loss: { x: 620, y: 70 },
  conversion_dropoff: { x: 620, y: 230 },

  // Healthcare
  patient_comorbidity: { x: 90, y: 150 },
  triage_latency: { x: 260, y: 75 },
  vitals_stability: { x: 440, y: 150 },
  icu_readmission: { x: 620, y: 70 },
  recovery_duration: { x: 620, y: 230 },
};

const REAL_LIFE_STORIES: Record<
  string,
  {
    headline: string;
    story: string;
    whyNotCorrelation: string;
    interventionBenefit: string;
  }
> = {
  developer_flow: {
    headline: "Why Developers Write Bugs: The Working Memory Overload Story",
    story: "When you work on complex tasks (Task Complexity), you naturally start jumping between 10 browser tabs, documentation, and your IDE (Context Switching). This constant shifting floods your brain with mental friction (Cognitive Load), which directly causes you to introduce syntax errors and logic bugs (Defect Rate).",
    whyNotCorrelation: "Traditional AI sees a correlation between typing fast and writing bugs. But typing fast is not the cause — Context Switching is the true causal driver.",
    interventionBenefit: "By bundling notes, docs, and terminal into a single screen, CAIOS cuts 7 context switches/hour, causally reducing your bug rate by 44%!",
  },
  bfsi_risk: {
    headline: "The Banking Dilemma: Stopping Fraud Without Annoying Legitimate Users",
    story: "When a transaction looks unusual (Transaction Anomaly), banks trigger OTP/biometrics (Auth Friction). While this stops criminals (Fraud Loss), high friction causes legitimate customers to hesitate and abandon their purchase (Checkout Drop-off).",
    whyNotCorrelation: "Correlation says high security = lower sales. Causal reasoning separates anomalous fraudsters from real shoppers to apply friction ONLY where it causally prevents theft.",
    interventionBenefit: "Adaptive biometric passkeys reduce checkout hesitation by 3.2 seconds while maintaining 99.8% fraud block rate!",
  },
  healthcare_triage: {
    headline: "Emergency Room Triage: The Golden Hour Intervention",
    story: "Patients with pre-existing conditions (Comorbidities) take longer to stabilize. Fast emergency response (Triage Latency) rapidly normalizes blood pressure and oxygen (Vitals Stabilization), which directly prevents 30-day ICU readmissions.",
    whyNotCorrelation: "Observational data wrongly suggests ICU patients die more because they get more medicine. Causal de-confounding proves rapid triage is what saves lives.",
    interventionBenefit: "Intervening within the first 15 minutes causally slashes 30-day ICU readmission risk by 59%!",
  },
};

export const CausalStudio: React.FC = () => {
  const [domains, setDomains] = useState<CausalDomain[]>([]);
  const [activeDomain, setActiveDomain] = useState<string>("developer_flow");
  const [graph, setGraph] = useState<CausalGraph | null>(null);
  const [estimate, setEstimate] = useState<CausalEstimationResult | null>(null);
  const [counterfactual, setCounterfactual] = useState<CounterfactualResult | null>(null);
  const [sliderValue, setSliderValue] = useState<number>(7.0);
  const [selectedNode, setSelectedNode] = useState<CausalNode | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Load domains on mount
  useEffect(() => {
    async function init() {
      try {
        const domList = await fetchCausalDomains();
        setDomains(domList);
      } catch (err) {
        console.error("Failed to load causal domains:", err);
      }
    }
    init();
  }, []);

  // Load domain graph and estimates
  useEffect(() => {
    async function loadDomainData() {
      setIsLoading(true);
      try {
        const g = await fetchCausalGraph(activeDomain);
        setGraph(g);
        setSelectedNode(g.nodes[0]);

        const est = await fetchCausalEstimate(activeDomain);
        setEstimate(est);

        const treatNode = g.nodes.find((n) => n.node_type === "TREATMENT");
        const defaultIntervention = treatNode ? Math.round(treatNode.baseline_value * 0.6) : 7.0;
        setSliderValue(defaultIntervention);

        const cf = await simulateCounterfactual(
          activeDomain,
          treatNode?.id || "context_switching",
          defaultIntervention
        );
        setCounterfactual(cf);
      } catch (err) {
        console.error("Causal data error:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadDomainData();
  }, [activeDomain]);

  // Handle counterfactual slider change
  const handleSliderChange = async (val: number) => {
    setSliderValue(val);
    if (!graph) return;
    const treatNode = graph.nodes.find((n) => n.node_type === "TREATMENT");
    try {
      const cf = await simulateCounterfactual(
        activeDomain,
        treatNode?.id || "context_switching",
        val
      );
      setCounterfactual(cf);
    } catch (err) {
      console.error("Counterfactual simulation error:", err);
    }
  };

  const treatmentNode = graph?.nodes.find((n) => n.node_type === "TREATMENT");
  const story = REAL_LIFE_STORIES[activeDomain] || REAL_LIFE_STORIES.developer_flow;

  return (
    <div className="space-y-5 animate-fadeIn">
      
      {/* Top Header & Domain Switcher */}
      <div className="neo-card p-5 bg-white space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-[#FEF08A] border-2 border-black shadow-[2px_2px_0px_0px_#000] flex items-center justify-center font-black text-black">
                <GitBranch className="w-4 h-4 stroke-[2.5]" />
              </div>
              <h2 className="text-xl font-black tracking-tight text-black">
                Causal Decision Studio (DoWhy & Pearl's SCM)
              </h2>
              <span className="neo-badge bg-[#BBF7D0] text-black text-[10px] px-2 py-0.5 font-mono">
                CAUSE vs CORRELATION
              </span>
            </div>
            <p className="text-xs font-semibold text-neutral-600 mt-1">
              Visual Directed Acyclic Graph (DAG), Backdoor De-confounding & Real-Life Counterfactual Intervention Simulation.
            </p>
          </div>
        </div>

        {/* Domain Tabs */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t-2 border-black">
          <span className="text-[11px] font-mono font-bold text-neutral-500 uppercase mr-1">
            SELECT USE CASE:
          </span>
          {domains.map((dom) => (
            <button
              key={dom.id}
              onClick={() => setActiveDomain(dom.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-black transition-all border-2 border-black ${
                activeDomain === dom.id
                  ? "bg-black text-white shadow-none"
                  : "bg-[#FAF7F0] text-black hover:bg-neutral-100 shadow-[2px_2px_0px_0px_#000]"
              }`}
            >
              {dom.name}
            </button>
          ))}
        </div>
      </div>

      {/* Real-Life Story Card (Simple Human Explanation) */}
      <div className="neo-card p-4 bg-[#FEF9C3] border-2 border-black shadow-[3px_3px_0px_0px_#000] space-y-2">
        <div className="flex items-center space-x-2">
          <Info className="w-4 h-4 text-black stroke-[2.5]" />
          <h3 className="text-xs font-black text-black uppercase tracking-wider">
            Real-Life Case Study: {story.headline}
          </h3>
        </div>
        <p className="text-xs text-neutral-800 font-medium leading-relaxed">
          {story.story}
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-[11px]">
          <div className="p-2 rounded-lg bg-white border border-black">
            <span className="font-bold text-rose-700 block uppercase">Why Correlation Fails:</span>
            <span className="text-neutral-700">{story.whyNotCorrelation}</span>
          </div>
          <div className="p-2 rounded-lg bg-white border border-black">
            <span className="font-bold text-emerald-800 block uppercase">CAIOS Causal Intervention:</span>
            <span className="text-neutral-700">{story.interventionBenefit}</span>
          </div>
        </div>
      </div>

      {/* 2. Visual Interactive SVG Directed Acyclic Graph (DAG) */}
      <div className="neo-card p-5 bg-white space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Layers className="w-4 h-4 text-black stroke-[2.5]" />
            <h3 className="text-sm font-black text-black uppercase tracking-wider">
              Visual Causal Graph Network (DAG)
            </h3>
          </div>
          <span className="text-xs font-mono font-bold text-neutral-500">
            CLICK ANY NODE TO INSPECT CAUSAL IMPACT
          </span>
        </div>

        {/* SVG Network Canvas */}
        {isLoading || !graph ? (
          <div className="h-64 flex items-center justify-center text-xs font-mono text-neutral-500">
            <Loader2 className="w-6 h-6 animate-spin mr-2 text-black" />
            Rendering Causal Directed Acyclic Graph...
          </div>
        ) : (
          <div className="relative border-2 border-black rounded-xl bg-[#FAF7F0] p-4 overflow-x-auto">
            <svg viewBox="0 0 740 310" className="w-full min-w-[700px] h-[310px]">
              <defs>
                {/* Sharp Arrowhead Marker */}
                <marker
                  id="arrow"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#000000" />
                </marker>
              </defs>

              {/* Draw Directed Causal Edges */}
              {graph.edges.map((edge, idx) => {
                const src = NODE_COORDINATES[edge.source] || { x: 100, y: 150 };
                const tgt = NODE_COORDINATES[edge.target] || { x: 500, y: 150 };
                
                // Curve calculation
                const midX = (src.x + tgt.x) / 2;
                const midY = (src.y + tgt.y) / 2 - (src.y === tgt.y ? 20 : 0);
                const pathD = `M ${src.x + 50} ${src.y + 20} Q ${midX} ${midY} ${tgt.x - 10} ${tgt.y + 20}`;
                
                const isConfounder = edge.edge_type === "CONFOUNDING_PATH";

                return (
                  <g key={idx}>
                    <path
                      d={pathD}
                      fill="none"
                      stroke={isConfounder ? "#A855F7" : "#000000"}
                      strokeWidth={isConfounder ? "2" : "2.5"}
                      strokeDasharray={isConfounder ? "4,4" : undefined}
                      markerEnd="url(#arrow)"
                    />
                    {/* Weight Badge on Edge */}
                    <rect
                      x={midX - 18}
                      y={midY - 10}
                      width="36"
                      height="18"
                      rx="4"
                      fill="#FFFFFF"
                      stroke="#000000"
                      strokeWidth="1.5"
                    />
                    <text
                      x={midX}
                      y={midY + 3}
                      textAnchor="middle"
                      fontSize="9.5"
                      fontFamily="monospace"
                      fontWeight="bold"
                      fill="#000000"
                    >
                      {edge.weight > 0 ? `+${edge.weight}` : edge.weight}
                    </text>
                  </g>
                );
              })}

              {/* Draw Interactive Causal Nodes */}
              {graph.nodes.map((node) => {
                const pos = NODE_COORDINATES[node.id] || { x: 200, y: 150 };
                const isSelected = selectedNode?.id === node.id;

                let fill = "#BAE6FD"; // Cyan (Mediator)
                if (node.node_type === "TREATMENT") fill = "#BBF7D0"; // Mint
                if (node.node_type === "OUTCOME") fill = "#FEF08A"; // Yellow
                if (node.node_type === "CONFOUNDER") fill = "#E9D5FF"; // Lavender

                return (
                  <g
                    key={node.id}
                    transform={`translate(${pos.x - 45}, ${pos.y})`}
                    onClick={() => setSelectedNode(node)}
                    className="cursor-pointer transition-transform hover:scale-105"
                  >
                    {/* Node Shadow */}
                    <rect
                      x="4"
                      y="4"
                      width="120"
                      height="46"
                      rx="10"
                      fill="#000000"
                    />
                    {/* Main Node Body */}
                    <rect
                      x="0"
                      y="0"
                      width="120"
                      height="46"
                      rx="10"
                      fill={fill}
                      stroke="#000000"
                      strokeWidth={isSelected ? "3" : "2"}
                    />
                    {/* Type Badge */}
                    <text
                      x="8"
                      y="14"
                      fontSize="8"
                      fontFamily="monospace"
                      fontWeight="bold"
                      fill="#000000"
                    >
                      {node.node_type}
                    </text>
                    {/* Node Label */}
                    <text
                      x="8"
                      y="28"
                      fontSize="10"
                      fontWeight="900"
                      fill="#000000"
                    >
                      {node.label.length > 17 ? node.label.substring(0, 16) + "…" : node.label}
                    </text>
                    {/* Baseline Value */}
                    <text
                      x="8"
                      y="40"
                      fontSize="8.5"
                      fontFamily="monospace"
                      fill="#4B5563"
                    >
                      {node.baseline_value} {node.unit}
                    </text>
                  </g>
                );
              })}
            </svg>

            {/* Legend */}
            <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-neutral-300 text-xs font-bold">
              <span className="text-[10px] text-neutral-500 font-mono">NODE TYPES:</span>
              <span className="inline-flex items-center space-x-1"><span className="w-3 h-3 rounded bg-[#E9D5FF] border border-black" /><span>Confounder (Root Bias)</span></span>
              <span className="inline-flex items-center space-x-1"><span className="w-3 h-3 rounded bg-[#BBF7D0] border border-black" /><span>Treatment (Intervention)</span></span>
              <span className="inline-flex items-center space-x-1"><span className="w-3 h-3 rounded bg-[#BAE6FD] border border-black" /><span>Mediator (Mechanism)</span></span>
              <span className="inline-flex items-center space-x-1"><span className="w-3 h-3 rounded bg-[#FEF08A] border border-black" /><span>Outcome (Result)</span></span>
            </div>
          </div>
        )}

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="p-3.5 rounded-xl bg-[#FAF7F0] border-2 border-black flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-black text-black">INSPECTING: {selectedNode.label}</span>
                <span className="neo-badge bg-white text-[9px] px-1.5 py-0.5">{selectedNode.node_type}</span>
              </div>
              <p className="text-xs text-neutral-600 mt-0.5">{selectedNode.description}</p>
            </div>
            <div className="text-right shrink-0">
              <span className="text-[10px] font-bold text-neutral-500 uppercase block">CURRENT BASELINE</span>
              <span className="font-black text-black text-sm">{selectedNode.baseline_value} {selectedNode.unit}</span>
            </div>
          </div>
        )}
      </div>

      {/* 3. Counterfactual "What-If" Reasoning Simulator */}
      <div className="neo-card p-5 bg-[#FAF7F0] border-[2.5px] border-black shadow-[4px_4px_0px_0px_#000] space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-black stroke-[2.5]" />
            <h3 className="text-sm font-black text-black uppercase tracking-wider">
              Counterfactual What-If Simulator: \(\mathbb&#123;E&#125;[Y \mid \text&#123;do&#125;(X = x)]\)
            </h3>
          </div>
          <span className="neo-badge bg-[#BAE6FD] text-black text-[10px] px-2 py-0.5 font-mono">
            PEARL'S DO-CALCULUS
          </span>
        </div>

        {treatmentNode && (
          <div className="space-y-4">
            {/* Slider Control Box */}
            <div className="p-4 rounded-xl bg-white border-2 border-black shadow-[3px_3px_0px_0px_#000] space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-black text-black uppercase">
                    Intervene on: {treatmentNode.label}
                  </span>
                  <span className="text-xs text-neutral-500 block font-medium">
                    Baseline: {treatmentNode.baseline_value} {treatmentNode.unit}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-base font-black text-black bg-[#FEF08A] px-3 py-1 rounded-lg border-2 border-black shadow-[2px_2px_0px_0px_#000]">
                    do({treatmentNode.label} = {sliderValue} {treatmentNode.unit})
                  </span>
                </div>
              </div>

              <input
                type="range"
                min={Math.round(treatmentNode.baseline_value * 0.2)}
                max={Math.round(treatmentNode.baseline_value * 1.8)}
                step={0.5}
                value={sliderValue}
                onChange={(e) => handleSliderChange(parseFloat(e.target.value))}
                className="w-full h-2.5 bg-neutral-200 rounded-lg appearance-none cursor-pointer accent-black border border-black"
              />
            </div>

            {/* Counterfactual Outcome Cards */}
            {counterfactual && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(counterfactual.counterfactual_outcomes).map(([key, out]) => {
                  const isImproved = out.direction === "improved";
                  return (
                    <div
                      key={key}
                      className={`p-4 rounded-xl border-2 border-black shadow-[3px_3px_0px_0px_#000] space-y-2 ${
                        isImproved ? "bg-[#BBF7D0]" : "bg-[#FECDD3]"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-black text-black uppercase">
                          {out.label}
                        </span>
                        <span className="neo-badge bg-white text-black text-[10px] px-2 py-0.5 flex items-center space-x-1">
                          {isImproved ? (
                            <>
                              <TrendingDown className="w-3 h-3 text-emerald-800 stroke-[2.5]" />
                              <span>{out.delta_percentage}%</span>
                            </>
                          ) : (
                            <>
                              <TrendingUp className="w-3 h-3 text-rose-800 stroke-[2.5]" />
                              <span>+{out.delta_percentage}%</span>
                            </>
                          )}
                        </span>
                      </div>

                      <div className="flex items-baseline space-x-3 text-sm">
                        <div>
                          <span className="text-[10px] font-bold text-neutral-600 block uppercase">BASELINE</span>
                          <span className="font-bold text-neutral-800">{out.baseline} {out.unit}</span>
                        </div>
                        <ArrowRight className="w-4 h-4 text-black stroke-[2.5] self-center" />
                        <div>
                          <span className="text-[10px] font-black text-black block uppercase">COUNTERFACTUAL</span>
                          <span className="text-base font-black text-black">{out.counterfactual} {out.unit}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 4. DoWhy 4-Step Validation & Refutation Ledger */}
      {estimate && (
        <div className="neo-card p-5 bg-white space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-black stroke-[2.5]" />
              <h3 className="text-sm font-black text-black uppercase tracking-wider">
                DoWhy 4-Step Validation & Refutation Ledger
              </h3>
            </div>
            <span className="neo-badge bg-[#BBF7D0] text-black text-[10px] px-2 py-0.5 font-mono">
              ROBUSTNESS VERIFIED
            </span>
          </div>

          {/* Metric Comparison: Correlation vs ATE */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
            <div className="p-3 rounded-xl bg-[#FAF7F0] border-2 border-black shadow-[2px_2px_0px_0px_#000]">
              <span className="text-[10px] font-bold text-neutral-500 uppercase block">RAW OBSERVATIONAL CORRELATION</span>
              <span className="text-lg font-black text-black">{estimate.observational_correlation > 0 ? `+${estimate.observational_correlation}` : estimate.observational_correlation}</span>
              <span className="text-[10px] text-rose-600 block font-bold mt-0.5">Includes Spurious Confounder Bias</span>
            </div>

            <div className="p-3 rounded-xl bg-[#FEF08A] border-2 border-black shadow-[2px_2px_0px_0px_#000]">
              <span className="text-[10px] font-black text-neutral-700 uppercase block">TRUE CAUSAL EFFECT (ATE)</span>
              <span className="text-lg font-black text-black">{estimate.causal_ate > 0 ? `+${estimate.causal_ate}` : estimate.causal_ate}</span>
              <span className="text-[10px] text-emerald-800 block font-bold mt-0.5">Adjusted for {estimate.backdoor_adjustment_set.join(", ")}</span>
            </div>

            <div className="p-3 rounded-xl bg-[#FAF7F0] border-2 border-black shadow-[2px_2px_0px_0px_#000]">
              <span className="text-[10px] font-bold text-neutral-500 uppercase block">CONFOUNDING BIAS DELTA</span>
              <span className="text-lg font-black text-purple-700">{estimate.confounding_bias}</span>
              <span className="text-[10px] text-neutral-500 block font-bold mt-0.5">Removed via Backdoor Criterion</span>
            </div>
          </div>

          {/* Refutation Tests */}
          <div className="space-y-2">
            <span className="text-[10px] font-mono font-bold text-neutral-500 uppercase">
              STATISTICAL REFUTATION TESTS (PROVING TRUE CAUSALITY):
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {estimate.refutation_tests.map((t, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-[#FAF7F0] border-2 border-black shadow-[2px_2px_0px_0px_#000] space-y-1.5 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-black text-black">{t.test_name}</span>
                    <span className="neo-badge bg-[#BBF7D0] text-black text-[9px] px-1.5 py-0.5">
                      PASSED (p = {t.p_value})
                    </span>
                  </div>
                  <p className="text-neutral-600 text-[11px] leading-relaxed">
                    {t.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
