import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from ..config import settings
from ..models.action import ActionPayload, ActionLogEntry

logger = logging.getLogger("caios.audit")

def log_action_pre_execution(action: ActionPayload, status: str = "PENDING_EXECUTION", details: str = "") -> ActionLogEntry:
    """
    Logs every action to ./data/actions.log BEFORE execution takes place.
    Enforces Hard Safety Constraint #4.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    entry = ActionLogEntry(
        timestamp=timestamp,
        action_type=action.action_type.value,
        title=action.title,
        description=action.description,
        params=action.params,
        status=status,
        details=details
    )
    
    log_line = json.dumps(entry.model_dump()) + "\n"
    
    try:
        settings.ACTIONS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.ACTIONS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        logger.error(f"Failed to write to actions.log: {e}")
        
    return entry

def update_action_log_status(action: ActionPayload, status: str, details: str = "") -> ActionLogEntry:
    """Logs the final execution status (e.g. EXECUTED, FAILED, BLOCKED)."""
    return log_action_pre_execution(action, status=status, details=details)

def read_recent_logs(limit: int = 50) -> List[ActionLogEntry]:
    """Reads the most recent action log entries from actions.log."""
    if not settings.ACTIONS_LOG_PATH.exists():
        return []
    
    entries = []
    try:
        with open(settings.ACTIONS_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entries.append(ActionLogEntry(**data))
                    if len(entries) >= limit:
                        break
                except Exception:
                    continue
    except Exception as e:
        logger.error(f"Error reading actions.log: {e}")
        
    return entries
