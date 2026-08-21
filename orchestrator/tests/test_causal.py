import pytest
from fastapi.testclient import TestClient
from orchestrator.app.main import app
from orchestrator.app.core.causal_engine import causal_engine, NodeType

client = TestClient(app)

def test_causal_domains():
    resp = client.get("/causal/domains")
    assert resp.status_code == 200
    domains = resp.json()
    assert len(domains) >= 3
    domain_ids = [d["id"] for d in domains]
    assert "developer_flow" in domain_ids
    assert "bfsi_risk" in domain_ids
    assert "healthcare_triage" in domain_ids

def test_causal_graph_structure():
    resp = client.get("/causal/graph?domain=developer_flow")
    assert resp.status_code == 200
    graph = resp.json()
    assert graph["domain"] == "developer_flow"
    assert len(graph["nodes"]) >= 4
    assert len(graph["edges"]) >= 4
    
    node_types = [n["node_type"] for n in graph["nodes"]]
    assert NodeType.TREATMENT in node_types
    assert NodeType.OUTCOME in node_types
    assert NodeType.CONFOUNDER in node_types

def test_causal_estimation_dowhy_pipeline():
    resp = client.post("/causal/estimate", json={
        "domain": "developer_flow",
        "treatment": "context_switching",
        "outcome": "bug_rate"
    })
    assert resp.status_code == 200
    res = resp.json()
    assert res["domain"] == "developer_flow"
    assert res["treatment"] == "context_switching"
    assert res["causal_ate"] is not None
    assert res["observational_correlation"] is not None
    assert len(res["refutation_tests"]) == 2
    
    # Check that both Placebo and Common Cause refutations passed
    assert all(t["is_valid"] for t in res["refutation_tests"])
    assert "task_complexity" in res["backdoor_adjustment_set"]

def test_counterfactual_simulation():
    resp = client.post("/causal/counterfactual", json={
        "domain": "developer_flow",
        "treatment_variable": "context_switching",
        "intervened_value": 7.0
    })
    assert resp.status_code == 200
    res = resp.json()
    assert res["domain"] == "developer_flow"
    assert res["intervened_treatment_value"] == 7.0
    assert "bug_rate" in res["counterfactual_outcomes"]
    assert "deep_work_time" in res["counterfactual_outcomes"]
    
    # Reducing context switching from 14 to 7 (-50%) should improve outcomes
    bug_res = res["counterfactual_outcomes"]["bug_rate"]
    assert bug_res["counterfactual"] < bug_res["baseline"]
    assert bug_res["direction"] == "improved"
