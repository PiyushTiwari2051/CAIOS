import {
  ContextState,
  SuggestionResponse,
  ActionPayload,
  ActionExecutionResult,
  ActionLogEntry,
  ModeType,
  CausalDomain,
  CausalGraph,
  CausalEstimationResult,
  CounterfactualResult,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "http://127.0.0.1:8000";

export async function fetchCurrentContext(): Promise<ContextState> {
  const res = await fetch(`${API_BASE}/context/current`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch context: ${res.statusText}`);
  return res.json();
}

export async function fetchSuggestions(
  mode?: ModeType,
  prompt?: string,
  active_window?: string,
  process_name?: string
): Promise<SuggestionResponse> {
  const res = await fetch(`${API_BASE}/suggest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode, prompt, active_window, process_name }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to fetch suggestions: ${res.statusText}`);
  return res.json();
}

export async function executeAction(
  action: ActionPayload,
  overrideKillswitch = false
): Promise<ActionExecutionResult> {
  const res = await fetch(`${API_BASE}/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, override_killswitch: overrideKillswitch }),
    cache: "no-store",
  });
  
  if (res.status === 423) {
    const errorData = await res.json();
    return {
      success: false,
      action_type: action.action_type,
      title: action.title,
      message: errorData.detail?.message || "Execution blocked: Emergency Kill Switch is active!",
      timestamp: new Date().toISOString(),
      details: { blocked_by_killswitch: true }
    };
  }
  
  if (!res.ok) {
    throw new Error(`Execution error: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchActionLogs(limit = 30): Promise<ActionLogEntry[]> {
  const res = await fetch(`${API_BASE}/log?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch logs: ${res.statusText}`);
  return res.json();
}

export async function toggleKillSwitch(): Promise<{ is_active: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/killswitch/toggle`, {
    method: "POST",
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to toggle kill switch: ${res.statusText}`);
  return res.json();
}

export async function setModeOverride(mode: ModeType | null): Promise<any> {
  if (mode === null) {
    const res = await fetch(`${API_BASE}/mode/override`, {
      method: "DELETE",
      cache: "no-store",
    });
    return res.json();
  } else {
    const res = await fetch(`${API_BASE}/mode/override`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
      cache: "no-store",
    });
    return res.json();
  }
}

// Causal Inference API Client
export async function fetchCausalDomains(): Promise<CausalDomain[]> {
  const res = await fetch(`${API_BASE}/causal/domains`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch causal domains: ${res.statusText}`);
  return res.json();
}

export async function fetchCausalGraph(domain = "developer_flow"): Promise<CausalGraph> {
  const res = await fetch(`${API_BASE}/causal/graph?domain=${domain}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch causal graph: ${res.statusText}`);
  return res.json();
}

export async function fetchCausalEstimate(
  domain = "developer_flow",
  treatment = "context_switching",
  outcome = "bug_rate"
): Promise<CausalEstimationResult> {
  const res = await fetch(`${API_BASE}/causal/estimate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain, treatment, outcome }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to estimate causal effect: ${res.statusText}`);
  return res.json();
}

export async function simulateCounterfactual(
  domain = "developer_flow",
  treatment_variable = "context_switching",
  intervened_value = 7.0
): Promise<CounterfactualResult> {
  const res = await fetch(`${API_BASE}/causal/counterfactual`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain, treatment_variable, intervened_value }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to simulate counterfactual: ${res.statusText}`);
  return res.json();
}
