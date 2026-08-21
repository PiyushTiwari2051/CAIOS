from typing import Dict, Any, Optional
from .base import BaseLLMProvider

class MockHeuristicProvider(BaseLLMProvider):
    """
    Guarantees deterministic, high-quality responses for offline demos,
    tests, or when local LLM server is not running.
    """
    async def generate_reasoning(
        self,
        mode: str,
        user_request: Optional[str] = None,
        active_window: Optional[str] = None,
        process_name: Optional[str] = None
    ) -> Dict[str, Any]:
        mode_upper = mode.upper()
        req_lower = (user_request or "").lower()

        if "doc" in req_lower or "api" in req_lower or "read" in req_lower:
            return {
                "reasoning": f"User requested documentation while in {mode_upper} mode. Surfacing developer references.",
                "actions": [
                    {
                        "action_type": "OPEN_URL",
                        "title": "Open FastApi Docs",
                        "description": "Navigate to FastAPI documentation",
                        "params": {"url": "https://fastapi.tiangolo.com"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "CREATE_NOTE",
                        "title": "API Research Notes",
                        "description": "Initialize API research scratchpad",
                        "params": {"filename": "api_notes.md", "content": "# API Integration Notes\n- Endpoints:\n- Schemas:\n"},
                        "requires_confirmation": True
                    }
                ]
            }

        if mode_upper == "CODING":
            return {
                "reasoning": f"Detected developer workspace ({process_name or 'code.exe'}). Optimizing environment for coding flow.",
                "actions": [
                    {
                        "action_type": "OPEN_URL",
                        "title": "Open GitHub Dashboard",
                        "description": "Check pull requests and repository activity",
                        "params": {"url": "https://github.com"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "OPEN_APP",
                        "title": "Launch Terminal",
                        "description": "Open developer terminal for build commands",
                        "params": {"app": "terminal"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "CREATE_NOTE",
                        "title": "Init Feature Checklist",
                        "description": "Create task checklist in sandbox notes",
                        "params": {"filename": "coding_tasks.md", "content": "# Sprint Tasks\n- [ ] Core implementation\n- [ ] Unit tests\n- [ ] Documentation\n"},
                        "requires_confirmation": True
                    }
                ]
            }
        elif mode_upper == "WRITING":
            return {
                "reasoning": "Detected writing / drafting context. Setting up distraction-free drafting tools.",
                "actions": [
                    {
                        "action_type": "CREATE_NOTE",
                        "title": "Create Draft Document",
                        "description": "Initialize clean markdown draft in sandbox",
                        "params": {"filename": "document_draft.md", "content": "# New Draft\n\n## Abstract\n\n## Outline\n- Introduction\n- Body\n- Conclusion\n"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "SET_REMINDER",
                        "title": "Focus Session (25m)",
                        "description": "Start 25-minute Pomodoro focus block",
                        "params": {"seconds": 1500, "message": "Focus sprint complete! Take a 5-minute break."},
                        "requires_confirmation": True
                    }
                ]
            }
        elif mode_upper == "STUDYING":
            return {
                "reasoning": "Detected academic / studying context. Surfacing research references and summary tools.",
                "actions": [
                    {
                        "action_type": "OPEN_URL",
                        "title": "ArXiv Computer Science",
                        "description": "Browse latest publications in AI & Systems",
                        "params": {"url": "https://arxiv.org/list/cs.AI/recent"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "CREATE_NOTE",
                        "title": "Study Notes",
                        "description": "Create lecture key takeaways note",
                        "params": {"filename": "study_notes.md", "content": "# Study Session Notes\n\n### Key Concepts:\n- \n\n### Open Questions:\n- \n"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "SET_REMINDER",
                        "title": "Study Timer (30m)",
                        "description": "Remind to stretch and hydrate in 30 minutes",
                        "params": {"seconds": 1800, "message": "Study block finished. Rest eyes and hydrate."},
                        "requires_confirmation": True
                    }
                ]
            }
        elif mode_upper == "MEETING":
            return {
                "reasoning": "Detected meeting / video conference context. Preparing action item capture.",
                "actions": [
                    {
                        "action_type": "CREATE_NOTE",
                        "title": "Meeting Action Items",
                        "description": "Open live meeting minutes template",
                        "params": {"filename": "meeting_action_items.md", "content": "# Meeting Minutes\n**Date:** Today\n**Attendees:**\n\n### Key Decisions\n- \n\n### Action Items\n- [ ] "},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "SET_REMINDER",
                        "title": "Meeting Follow-up Reminder",
                        "description": "Remind to send summary email in 45 minutes",
                        "params": {"seconds": 2700, "message": "Follow up on meeting action items."},
                        "requires_confirmation": True
                    }
                ]
            }
        else: # IDLE
            return {
                "reasoning": "System is in ambient / idle mode. Offering quick launcher shortcuts.",
                "actions": [
                    {
                        "action_type": "OPEN_URL",
                        "title": "Hacker News",
                        "description": "Browse today's top tech discussions",
                        "params": {"url": "https://news.ycombinator.com"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "OPEN_APP",
                        "title": "Play Focus Music",
                        "description": "Launch Spotify for focus soundtrack",
                        "params": {"app": "spotify"},
                        "requires_confirmation": True
                    }
                ]
            }
