from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from ..core.causal_engine import (
    causal_engine,
    CausalGraph,
    CausalEstimationResult,
    CounterfactualSimulationResult
)

router = APIRouter(prefix="/causal", tags=["Causal AI"])

class CounterfactualRequest(BaseModel):
    domain: str = Field("developer_flow", description="Target domain model")
    treatment_variable: str = Field("context_switching", description="Treatment variable to intervene upon")
    intervened_value: float = Field(7.0, description="Target value for do(X = x)")

class EstimateRequest(BaseModel):
    domain: str = Field("developer_flow", description="Target domain model")
    treatment: str = Field("context_switching", description="Treatment variable")
    outcome: str = Field("bug_rate", description="Outcome variable")

@router.get("/domains")
async def list_domains():
    """Returns available pre-tuned causal domain templates (Developer Flow, BFSI, Healthcare)."""
    return [
        {
            "id": "developer_flow",
            "name": "Developer Flow & Workspace Control",
            "description": "Causal DAG modeling IDE context switching vs mental friction and defect ingestion rate."
        },
        {
            "id": "bfsi_risk",
            "name": "BFSI Adaptive Risk & Fraud Intelligence",
            "description": "Causal DAG balancing real-time MFA authentication friction against fraud exposure and checkout drop-off."
        },
        {
            "id": "healthcare_triage",
            "name": "Clinical Triage & Patient Outcome Causality",
            "description": "Causal inference graph identifying true effect of emergency response latency on ICU readmission."
        }
    ]

@router.get("/graph", response_model=CausalGraph)
async def get_causal_graph(domain: str = Query("developer_flow")):
    """Returns the Directed Acyclic Graph (DAG) for a given domain."""
    return causal_engine.get_graph(domain)

@router.post("/estimate", response_model=CausalEstimationResult)
async def estimate_causal_pipeline(req: EstimateRequest):
    """
    Executes the complete 4-Step DoWhy Pipeline:
    1. Model (DAG) -> 2. Identify (Backdoor Adjustment) -> 3. Estimate (ATE) -> 4. Refute (Placebo & Confounder Tests)
    """
    return causal_engine.estimate_causal_effect(
        domain=req.domain,
        treatment=req.treatment,
        outcome=req.outcome
    )

@router.post("/counterfactual", response_model=CounterfactualSimulationResult)
async def simulate_counterfactual_intervention(req: CounterfactualRequest):
    """
    Computes Counterfactual 'What-If' Simulation: E[Y | do(X = x)].
    Simulates outcome distribution under active intervention.
    """
    return causal_engine.simulate_counterfactual(
        domain=req.domain,
        treatment_variable=req.treatment_variable,
        intervened_value=req.intervened_value
    )
