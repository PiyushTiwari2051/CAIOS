import pytest
from pydantic import ValidationError
from orchestrator.app.models.action import (
    ActionPayload,
    ActionType,
    AllowedApp,
    ActionExecutionRequest
)
from orchestrator.app.core.executor import executor
from orchestrator.app.core.killswitch import kill_switch
from orchestrator.app.config import settings

def test_valid_action_payloads():
    """Verify that all four allow-listed action types construct valid payloads."""
    # OPEN_APP
    app_action = ActionPayload(
        action_type=ActionType.OPEN_APP,
        title="Open Code",
        description="Launch editor",
        params={"app": "vscode"}
    )
    assert app_action.action_type == ActionType.OPEN_APP
    assert app_action.params["app"] == "vscode"

    # OPEN_URL
    url_action = ActionPayload(
        action_type=ActionType.OPEN_URL,
        title="Open ArXiv",
        description="Open papers",
        params={"url": "https://arxiv.org"}
    )
    assert url_action.action_type == ActionType.OPEN_URL

    # CREATE_NOTE
    note_action = ActionPayload(
        action_type=ActionType.CREATE_NOTE,
        title="Quick Note",
        description="Save summary",
        params={"filename": "test_note.md", "content": "Hello CAIOS"}
    )
    assert note_action.action_type == ActionType.CREATE_NOTE

    # SET_REMINDER
    reminder_action = ActionPayload(
        action_type=ActionType.SET_REMINDER,
        title="Break Reminder",
        description="Take rest",
        params={"seconds": 60, "message": "Time to stand up"}
    )
    assert reminder_action.action_type == ActionType.SET_REMINDER

def test_reject_arbitrary_or_malicious_action_types():
    """Hard Safety Constraint #3: Raw shell actions or invalid action types must fail validation."""
    with pytest.raises(ValidationError):
        ActionPayload(
            action_type="EXECUTE_SHELL",  # Not in ActionType enum
            title="Run arbitrary command",
            description="Danger",
            params={"command": "rm -rf /"}
        )

    with pytest.raises(ValidationError):
        ActionPayload(
            action_type="RUN_SCRIPT",
            title="Run script",
            description="Danger",
            params={"script": "powershell.exe"}
        )

def test_reject_unauthorized_apps():
    """OPEN_APP must reject executables not in AllowedApp."""
    with pytest.raises(ValidationError) as exc_info:
        ActionPayload(
            action_type=ActionType.OPEN_APP,
            title="Run Command Shell",
            description="Open cmd",
            params={"app": "cmd.exe"} # Must be explicitly in AllowedApp
        )
    assert "not in the allowed apps list" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        ActionPayload(
            action_type=ActionType.OPEN_APP,
            title="Run Powershell",
            description="Open pwsh",
            params={"app": "powershell"}
        )
    assert "not in the allowed apps list" in str(exc_info.value)

def test_reject_dangerous_url_schemes():
    """OPEN_URL must reject non-http/https schemes."""
    with pytest.raises(ValidationError):
        ActionPayload(
            action_type=ActionType.OPEN_URL,
            title="Local File Access",
            description="Attempt file read",
            params={"url": "file:///C:/Windows/System32/drivers/etc/hosts"}
        )

    with pytest.raises(ValidationError):
        ActionPayload(
            action_type=ActionType.OPEN_URL,
            title="Javascript execution",
            description="XSS attempt",
            params={"url": "javascript:alert(1)"}
        )

def test_reject_path_traversal_in_notes():
    """CREATE_NOTE must reject relative directory traversal."""
    with pytest.raises(ValidationError) as exc_info:
        ActionPayload(
            action_type=ActionType.CREATE_NOTE,
            title="Escape sandbox",
            description="Traversal attempt",
            params={"filename": "../../escaped.txt", "content": "bad"}
        )
    assert "Path traversal and separators are forbidden" in str(exc_info.value)

def test_create_note_execution_in_sandbox():
    """Verifies that CREATE_NOTE writes strictly to the ./sandbox/notes folder."""
    action = ActionPayload(
        action_type=ActionType.CREATE_NOTE,
        title="Unit Test Note",
        description="Verify disk writing in sandbox",
        params={"filename": "unit_test_note.md", "content": "Sandbox Isolation Confirmed"}
    )
    result = executor.execute(action)
    assert result.success is True

    note_path = settings.SANDBOX_PATH / "notes" / "unit_test_note.md"
    assert note_path.exists()
    with open(note_path, "r", encoding="utf-8") as f:
        assert f.read() == "Sandbox Isolation Confirmed"

def test_killswitch_blocks_execution():
    """Verifies that active kill switch halts action execution and logs blocked event."""
    kill_switch.set_active(True)
    try:
        action = ActionPayload(
            action_type=ActionType.OPEN_URL,
            title="Blocked URL",
            description="Should not execute",
            params={"url": "https://example.com"}
        )
        result = executor.execute(action)
        assert result.success is False
        assert "emergency kill switch is currently ACTIVE" in result.message
    finally:
        kill_switch.set_active(False)
