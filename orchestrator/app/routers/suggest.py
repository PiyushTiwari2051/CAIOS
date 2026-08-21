import httpx
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from ..config import settings
from ..models.mode import ModeEnum
from ..models.action import ActionPayload, ActionType, AllowedApp
from ..core.classifier import DEFAULT_MODE_ASSETS

router = APIRouter(prefix="/suggest", tags=["Suggestions"])

class SuggestionRequest(BaseModel):
    mode: Optional[ModeEnum] = None
    prompt: Optional[str] = None
    active_window: Optional[str] = None
    process_name: Optional[str] = None

class SuggestionResponse(BaseModel):
    mode: ModeEnum
    suggestions: List[ActionPayload]
    source: str # "llm_sandbox" or "rule_fallback"
    reasoning: Optional[str] = None

def get_default_suggestions_for_mode(mode: ModeEnum) -> List[ActionPayload]:
    """Fallback suggestions if sandbox container is still booting or offline."""
    if mode == ModeEnum.CODING:
        return [
            ActionPayload(
                action_type=ActionType.OPEN_URL,
                title="Open GitHub",
                description="Open GitHub dashboard for active repositories",
                params={"url": "https://github.com"}
            ),
            ActionPayload(
                action_type=ActionType.OPEN_APP,
                title="Launch Terminal",
                description="Open system developer terminal",
                params={"app": "terminal"}
            ),
            ActionPayload(
                action_type=ActionType.CREATE_NOTE,
                title="Create Dev Scratchpad",
                description="Initialize a clean markdown scratchpad for coding notes",
                params={"filename": "coding_scratchpad.md", "content": "# Coding Scratchpad\n- Task:\n- Notes:\n"}
            ),
        ]
    elif mode == ModeEnum.WRITING:
        return [
            ActionPayload(
                action_type=ActionType.CREATE_NOTE,
                title="Create New Draft",
                description="Start a new drafting note in sandbox",
                params={"filename": "draft_note.md", "content": "# Document Draft\n\nDate: " + datetime_stamp()}
            ),
            ActionPayload(
                action_type=ActionType.SET_REMINDER,
                title="Set Focus Timer (25m)",
                description="25-minute Pomodoro focus block for writing",
                params={"seconds": 1500, "message": "Pomodoro block complete! Take a 5-minute break."}
            ),
        ]
    elif mode == ModeEnum.STUDYING:
        return [
            ActionPayload(
                action_type=ActionType.OPEN_URL,
                title="Explore arXiv CS/AI",
                description="Browse latest research papers",
                params={"url": "https://arxiv.org/list/cs.AI/recent"}
            ),
            ActionPayload(
                action_type=ActionType.CREATE_NOTE,
                title="Study Summary Notes",
                description="Create lecture & reading summary note",
                params={"filename": "study_summary.md", "content": "# Study Summary\n## Key Concepts\n1. \n\n## Questions\n- "}
            ),
            ActionPayload(
                action_type=ActionType.SET_REMINDER,
                title="Study Break Reminder",
                description="Remind to hydrate and rest eyes in 30 minutes",
                params={"seconds": 1800, "message": "30 minutes elapsed. Stand up and hydrate!"}
            ),
        ]
    elif mode == ModeEnum.MEETING:
        return [
            ActionPayload(
                action_type=ActionType.CREATE_NOTE,
                title="Meeting Action Items",
                description="Create template for recording agenda and follow-ups",
                params={"filename": "meeting_notes.md", "content": "# Meeting Action Items\n**Date:** Today\n**Attendees:**\n\n### Decisions\n- \n\n### Action Items\n- [ ] "}
            ),
            ActionPayload(
                action_type=ActionType.SET_REMINDER,
                title="Send Meeting Follow-up",
                description="Reminder to send action item notes in 45 minutes",
                params={"seconds": 2700, "message": "Meeting ending soon. Send out summary notes."}
            ),
        ]
    else: # IDLE
        return [
            ActionPayload(
                action_type=ActionType.OPEN_URL,
                title="Check Tech News",
                description="Open Hacker News",
                params={"url": "https://news.ycombinator.com"}
            ),
            ActionPayload(
                action_type=ActionType.OPEN_APP,
                title="Open Music Player",
                description="Launch Spotify for ambient background focus",
                params={"app": "spotify"}
            )
        ]

def datetime_stamp() -> str:
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M")

@router.post("", response_model=SuggestionResponse)
async def generate_suggestions(request: SuggestionRequest):
    """
    Generates allow-listed suggestions by querying the isolated LLM sandbox.
    Falls back to deterministic rule suggestions if sandbox is loading or offline.
    """
    target_mode = request.mode or ModeEnum.IDLE
    
    # Attempt to query LLM Sandbox container
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(
                f"{settings.SANDBOX_URL}/reason",
                json={
                    "mode": target_mode.value,
                    "prompt": request.prompt,
                    "active_window": request.active_window,
                    "process_name": request.process_name
                }
            )
            
            if resp.status_code == 200:
                data = resp.json()
                raw_actions = data.get("actions", [])
                validated_actions: List[ActionPayload] = []
                
                # Strict allow-list validation on all LLM output
                for raw_act in raw_actions:
                    try:
                        validated_actions.append(ActionPayload(**raw_act))
                    except Exception:
                        continue # Drop any malformed or non-allowlisted action
                        
                if validated_actions:
                    return SuggestionResponse(
                        mode=target_mode,
                        suggestions=validated_actions,
                        source="llm_sandbox",
                        reasoning=data.get("reasoning", "Generated by LLM Sandbox")
                    )
    except Exception:
        pass
        
    fallback_actions = get_default_suggestions_for_mode(target_mode)
    return SuggestionResponse(
        mode=target_mode,
        suggestions=fallback_actions,
        source="rule_fallback",
        reasoning=f"Standard adaptive preset for {target_mode.value} mode"
    )
