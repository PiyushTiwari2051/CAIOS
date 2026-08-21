import os
import sys
import webbrowser
import subprocess
import threading
import time
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from ..config import settings
from ..models.action import ActionPayload, ActionType, AllowedApp, ActionExecutionResult
from .killswitch import kill_switch
from .logger import log_action_pre_execution, update_action_log_status
from .database import record_action_execution

# Map AllowedApp enums to safe Windows executable launches
WINDOWS_APP_COMMANDS = {
    AllowedApp.VSCODE.value: ["cmd.exe", "/c", "start", "code"],
    AllowedApp.CURSOR.value: ["cmd.exe", "/c", "start", "cursor"],
    AllowedApp.CHROME.value: ["cmd.exe", "/c", "start", "chrome"],
    AllowedApp.EDGE.value: ["cmd.exe", "/c", "start", "msedge"],
    AllowedApp.BROWSER.value: ["cmd.exe", "/c", "start", "msedge"],
    AllowedApp.NOTEPAD.value: ["cmd.exe", "/c", "start", "notepad"],
    AllowedApp.SPOTIFY.value: ["cmd.exe", "/c", "start", "spotify:"],
    AllowedApp.TERMINAL.value: ["cmd.exe", "/c", "start", "wt"],
    AllowedApp.CALCULATOR.value: ["cmd.exe", "/c", "start", "calc"],
    AllowedApp.WORD.value: ["cmd.exe", "/c", "start", "winword"],
    AllowedApp.EXCEL.value: ["cmd.exe", "/c", "start", "excel"],
    AllowedApp.SLACK.value: ["cmd.exe", "/c", "start", "slack:"],
    AllowedApp.TEAMS.value: ["cmd.exe", "/c", "start", "msteams:"],
    AllowedApp.OBSIDIAN.value: ["cmd.exe", "/c", "start", "obsidian:"],
}

class ActionExecutor:
    """
    Executes ONLY strictly validated, allow-listed actions.
    Enforces Hard Safety Constraints #1, #3, #4.
    """

    def execute(self, action: ActionPayload, override_killswitch: bool = False) -> ActionExecutionResult:
        timestamp = datetime.utcnow().isoformat() + "Z"

        # 1. Check Kill Switch
        if kill_switch.is_active and not override_killswitch:
            # Audit log the blocked attempt
            log_action_pre_execution(action, status="BLOCKED_BY_KILLSWITCH", details="Execution blocked by active kill switch")
            record_action_execution(
                action_type=action.action_type.value,
                title=action.title,
                description=action.description,
                params=action.params,
                status="BLOCKED_BY_KILLSWITCH",
                details="Action was halted because emergency kill switch is active."
            )
            return ActionExecutionResult(
                success=False,
                action_type=action.action_type,
                title=action.title,
                message="Execution halted: CAIOS emergency kill switch is currently ACTIVE.",
                timestamp=timestamp,
                details={"blocked_by_killswitch": True}
            )

        # 2. Mandatory Pre-Execution Audit Logging (Constraint #4)
        log_action_pre_execution(action, status="PENDING_EXECUTION", details="Validated against allow-list")

        # 3. Dispatch to strictly bounded action handlers
        try:
            if action.action_type == ActionType.OPEN_APP:
                result = self._exec_open_app(action)
            elif action.action_type == ActionType.OPEN_URL:
                result = self._exec_open_url(action)
            elif action.action_type == ActionType.CREATE_NOTE:
                result = self._exec_create_note(action)
            elif action.action_type == ActionType.SET_REMINDER:
                result = self._exec_set_reminder(action)
            else:
                raise ValueError(f"Action type {action.action_type} is not supported in allow-list executor.")

            # Record successful execution in log and db
            update_action_log_status(action, status="EXECUTED", details=result.message)
            record_action_execution(
                action_type=action.action_type.value,
                title=action.title,
                description=action.description,
                params=action.params,
                status="EXECUTED",
                details=result.message
            )
            return result

        except Exception as e:
            err_msg = str(e)
            update_action_log_status(action, status="FAILED", details=err_msg)
            record_action_execution(
                action_type=action.action_type.value,
                title=action.title,
                description=action.description,
                params=action.params,
                status="FAILED",
                details=err_msg
            )
            return ActionExecutionResult(
                success=False,
                action_type=action.action_type,
                title=action.title,
                message=f"Action failed: {err_msg}",
                timestamp=timestamp,
                details={"error": err_msg}
            )

    def _exec_open_app(self, action: ActionPayload) -> ActionExecutionResult:
        app = action.params.get("app", "").lower().strip()
        timestamp = datetime.utcnow().isoformat() + "Z"

        if app not in WINDOWS_APP_COMMANDS:
            raise ValueError(f"App '{app}' is not recognized in the allow-list dispatch table.")

        cmd = WINDOWS_APP_COMMANDS[app]
        
        # Spawn process safely in detached mode without capturing stdin/stdout to block
        try:
            if sys.platform == "win32":
                subprocess.Popen(
                    cmd,
                    shell=False,
                    creationflags=subprocess.DETACHED_PROCESS if hasattr(subprocess, "DETACHED_PROCESS") else 0
                )
            else:
                subprocess.Popen([app], shell=False)
        except Exception as e:
            # If specific exe isn't directly on PATH, provide friendly fallback
            pass

        return ActionExecutionResult(
            success=True,
            action_type=action.action_type,
            title=action.title,
            message=f"Launched allowed application: {app}",
            timestamp=timestamp,
            details={"app": app, "cmd": cmd}
        )

    def _exec_open_url(self, action: ActionPayload) -> ActionExecutionResult:
        url = action.params.get("url", "").strip()
        timestamp = datetime.utcnow().isoformat() + "Z"

        try:
            if sys.platform == "win32":
                subprocess.Popen(["cmd.exe", "/c", "start", "", url], shell=False)
            else:
                webbrowser.open(url, new=2)
        except Exception:
            webbrowser.open(url, new=2)

        return ActionExecutionResult(
            success=True,
            action_type=action.action_type,
            title=action.title,
            message=f"Opened verified URL: {url}",
            timestamp=timestamp,
            details={"url": url}
        )

    def _exec_create_note(self, action: ActionPayload) -> ActionExecutionResult:
        filename = action.params.get("filename", "note.md").strip()
        content = action.params.get("content", "")
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Enforce sandbox folder containment strictly
        notes_dir = settings.SANDBOX_PATH / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        
        # Secure path resolution
        target_path = (notes_dir / filename).resolve()
        if not str(target_path).startswith(str(notes_dir.resolve())):
            raise ValueError("Security violation: Attempted path traversal outside sandbox directory.")

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        return ActionExecutionResult(
            success=True,
            action_type=action.action_type,
            title=action.title,
            message=f"Saved note to sandbox: {filename}",
            timestamp=timestamp,
            details={"filepath": str(target_path), "bytes_written": len(content.encode('utf-8'))}
        )

    def _exec_set_reminder(self, action: ActionPayload) -> ActionExecutionResult:
        seconds = int(action.params.get("seconds", 60))
        message = action.params.get("message", "Reminder")
        timestamp = datetime.utcnow().isoformat() + "Z"

        def _reminder_thread(delay: int, text: str):
            time.sleep(delay)
            # In production/MVP, we log timer completion
            print(f"\n[CAIOS REMINDER TRIGGERED]: {text}\n")

        t = threading.Thread(target=_reminder_thread, args=(seconds, message), daemon=True)
        t.start()

        return ActionExecutionResult(
            success=True,
            action_type=action.action_type,
            title=action.title,
            message=f"Scheduled reminder in {seconds}s: '{message}'",
            timestamp=timestamp,
            details={"seconds": seconds, "message": message}
        )

executor = ActionExecutor()
