export type ModeType = "CODING" | "WRITING" | "STUDYING" | "MEETING" | "IDLE";

export type ActionType = "OPEN_APP" | "OPEN_URL" | "CREATE_NOTE" | "SET_REMINDER";

export interface ContextPayload {
  process_name: string;
  window_title: string;
  timestamp?: string;
  platform: string;
}

export interface ModeClassification {
  mode: ModeType;
  confidence: number;
  reasoning: string;
  is_manual_override: boolean;
  suggested_apps: string[];
  suggested_shortcuts: string[];
}

export interface ContextState {
  current_context: ContextPayload;
  current_mode: ModeClassification;
  manual_override: ModeType | null;
  last_updated: string;
  kill_switch_active: boolean;
}

export interface ActionPayload {
  action_type: ActionType;
  title: string;
  description: string;
  params: Record<string, any>;
  confidence?: number;
  requires_confirmation?: boolean;
}

export interface SuggestionResponse {
  mode: ModeType;
  suggestions: ActionPayload[];
  source: string;
  reasoning?: string;
}

export interface ActionExecutionResult {
  success: boolean;
  action_type: ActionType;
  title: string;
  message: string;
  timestamp: string;
  details?: Record<string, any>;
}

export interface ActionLogEntry {
  id?: number;
  timestamp: string;
  action_type: string;
  title: string;
  description: string;
  params: Record<string, any>;
  status: "LOGGED" | "EXECUTED" | "FAILED" | "BLOCKED_BY_KILLSWITCH" | "PENDING_EXECUTION";
  details?: string;
}

// Causal Inference AI Types
export interface CausalNode {
  id: string;
  label: string;
  node_type: "TREATMENT" | "OUTCOME" | "CONFOUNDER" | "MEDIATOR" | "COVARIATE";
  baseline_value: number;
  unit: string;
  description: string;
}

export interface CausalEdge {
  source: string;
  target: string;
  weight: number;
  edge_type: "DIRECT_CAUSE" | "CONFOUNDING_PATH" | "MEDIATION";
  confidence: number;
  is_spurious?: boolean;
}

export interface CausalGraph {
  domain: string;
  title: string;
  description: string;
  nodes: CausalNode[];
  edges: CausalEdge[];
}

export interface RefutationResult {
  test_name: string;
  original_effect: number;
  new_effect: number;
  p_value: number;
  is_valid: boolean;
  description: string;
}

export interface CausalEstimationResult {
  domain: string;
  treatment: string;
  outcome: string;
  observational_correlation: number;
  causal_ate: number;
  confounding_bias: number;
  identification_method: string;
  backdoor_adjustment_set: string[];
  refutation_tests: RefutationResult[];
  why_explanation: string;
  recommended_action: string;
}

export interface CounterfactualResult {
  domain: string;
  treatment_variable: string;
  baseline_treatment_value: number;
  intervened_treatment_value: number;
  percentage_change: number;
  counterfactual_outcomes: Record<
    string,
    {
      label: string;
      baseline: number;
      counterfactual: number;
      unit: string;
      delta_percentage: number;
      direction: "improved" | "worsened";
    }
  >;
  explanation: string;
}

export interface CausalDomain {
  id: string;
  name: string;
  description: string;
}
