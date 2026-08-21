from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
import re
from urllib.parse import urlparse

class ActionType(str, Enum):
    OPEN_APP = "OPEN_APP"
    OPEN_URL = "OPEN_URL"
    CREATE_NOTE = "CREATE_NOTE"
    SET_REMINDER = "SET_REMINDER"

class AllowedApp(str, Enum):
    VSCODE = "vscode"
    CURSOR = "cursor"
    CHROME = "chrome"
    EDGE = "edge"
    BROWSER = "browser"
    NOTEPAD = "notepad"
    SPOTIFY = "spotify"
    TERMINAL = "terminal"
    CALCULATOR = "calculator"
    WORD = "word"
    EXCEL = "excel"
    SLACK = "slack"
    TEAMS = "teams"
    OBSIDIAN = "obsidian"

class ActionPayload(BaseModel):
    action_type: ActionType
    title: str = Field(..., description="Short human-readable title of the action")
    description: str = Field(..., description="Explanation of why this action is suggested")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action specific parameters")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    requires_confirmation: bool = Field(default=True)

    @field_validator("params")
    @classmethod
    def validate_params(cls, params: Dict[str, Any], info) -> Dict[str, Any]:
        # Context will contain action_type if parsed
        action_type = info.data.get("action_type")
        if not action_type:
            return params

        if action_type == ActionType.OPEN_APP:
            app = params.get("app", "").lower().strip()
            if not app:
                raise ValueError("OPEN_APP requires 'app' parameter")
            # Must match allowed app enum values
            allowed_names = [a.value for a in AllowedApp]
            if app not in allowed_names:
                raise ValueError(f"App '{app}' is not in the allowed apps list: {allowed_names}")
            params["app"] = app

        elif action_type == ActionType.OPEN_URL:
            url = params.get("url", "").strip()
            if not url:
                raise ValueError("OPEN_URL requires 'url' parameter")
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                raise ValueError(f"Invalid or unsafe URL scheme/format: '{url}'. Only http/https URLs are permitted.")
            params["url"] = url

        elif action_type == ActionType.CREATE_NOTE:
            filename = params.get("filename", "").strip()
            content = params.get("content", "")
            if not filename:
                raise ValueError("CREATE_NOTE requires 'filename' parameter")
            # Strict filename validation: no path traversal or special directory separators
            if ".." in filename or "/" in filename or "\\" in filename:
                raise ValueError(f"Invalid note filename '{filename}'. Path traversal and separators are forbidden.")
            # Sanitize filename
            if not filename.endswith(".md") and not filename.endswith(".txt"):
                filename += ".md"
            params["filename"] = filename
            params["content"] = content

        elif action_type == ActionType.SET_REMINDER:
            seconds = params.get("seconds")
            message = params.get("message", "").strip()
            if seconds is None:
                raise ValueError("SET_REMINDER requires 'seconds' parameter")
            try:
                seconds_val = int(seconds)
                if seconds_val <= 0 or seconds_val > 86400: # Max 24 hours
                    raise ValueError("Reminder seconds must be between 1 and 86400")
                params["seconds"] = seconds_val
            except (ValueError, TypeError):
                raise ValueError("Reminder 'seconds' must be a valid positive integer")
            if not message:
                raise ValueError("SET_REMINDER requires non-empty 'message' parameter")
            params["message"] = message

        return params

class ActionExecutionRequest(BaseModel):
    action: ActionPayload
    override_killswitch: bool = False

class ActionExecutionResult(BaseModel):
    success: bool
    action_type: ActionType
    title: str
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class ActionLogEntry(BaseModel):
    id: Optional[int] = None
    timestamp: str
    action_type: str
    title: str
    description: str
    params: Dict[str, Any]
    status: str # "LOGGED", "EXECUTED", "REJECTED", "BLOCKED_BY_KILLSWITCH"
    details: Optional[str] = None
