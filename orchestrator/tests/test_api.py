import pytest
from fastapi.testclient import TestClient
from orchestrator.app.main import app
from orchestrator.app.core.killswitch import kill_switch

client = TestClient(app)

def setup_function():
    # Ensure kill switch is reset to False before each test
    kill_switch.set_active(False)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_post_context_and_mode_classification():
    payload = {
        "process_name": "code.exe",
        "window_title": "app.py - CAIOS Project",
        "platform": "windows"
    }
    response = client.post("/context", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["current_context"]["process_name"] == "code.exe"
    assert data["current_mode"]["mode"] == "CODING"
    assert data["current_mode"]["confidence"] >= 0.9

def test_get_current_context():
    response = client.get("/context/current")
    assert response.status_code == 200
    data = response.json()
    assert "current_mode" in data
    assert "kill_switch_active" in data

def test_post_suggest_endpoint():
    response = client.post("/suggest", json={"mode": "CODING", "prompt": "Need developer tools"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "CODING"
    assert len(data["suggestions"]) > 0
    # Every suggestion must have valid action_type
    for item in data["suggestions"]:
        assert item["action_type"] in ["OPEN_APP", "OPEN_URL", "CREATE_NOTE", "SET_REMINDER"]

def test_post_execute_and_audit_log():
    action_payload = {
        "action": {
            "action_type": "CREATE_NOTE",
            "title": "API Test Note",
            "description": "Integration test created note",
            "params": {
                "filename": "api_test.md",
                "content": "# Test content from API"
            },
            "requires_confirmation": True
        }
    }
    response = client.post("/execute", json=action_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True

    # Verify audit log contains entry
    log_response = client.get("/log?limit=5")
    assert log_response.status_code == 200
    logs = log_response.json()
    assert len(logs) > 0
    assert any(log["title"] == "API Test Note" for log in logs)

def test_killswitch_api_behavior():
    # 1. Activate killswitch via API
    toggle_resp = client.post("/killswitch/toggle")
    assert toggle_resp.status_code == 200
    assert toggle_resp.json()["is_active"] is True

    # 2. Try executing an action -> must return HTTP 423 Locked
    action_payload = {
        "action": {
            "action_type": "OPEN_URL",
            "title": "Test URL",
            "description": "Will be blocked",
            "params": {"url": "https://google.com"}
        }
    }
    exec_resp = client.post("/execute", json=action_payload)
    assert exec_resp.status_code == 423

    # 3. Deactivate killswitch
    toggle_resp2 = client.post("/killswitch/toggle")
    assert toggle_resp2.status_code == 200
    assert toggle_resp2.json()["is_active"] is False

def test_mode_override_api():
    # Set override to WRITING
    override_resp = client.post("/mode/override", json={"mode": "WRITING"})
    assert override_resp.status_code == 200
    assert override_resp.json()["is_override"] is True
    assert override_resp.json()["classification"]["mode"] == "WRITING"

    # Context update should respect override
    ctx_resp = client.post("/context", json={"process_name": "code.exe", "window_title": "editor"})
    assert ctx_resp.json()["current_mode"]["mode"] == "WRITING"

    # Clear override
    clear_resp = client.delete("/mode/override")
    assert clear_resp.status_code == 200

    # Context update now returns natural CODING mode
    ctx_resp2 = client.post("/context", json={"process_name": "code.exe", "window_title": "editor"})
    assert ctx_resp2.json()["current_mode"]["mode"] == "CODING"
