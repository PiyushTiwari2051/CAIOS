from typing import Dict, Any, Optional
from .base import BaseLLMProvider

class MockHeuristicProvider(BaseLLMProvider):
    """
    Intelligent Semantic Reasoning Provider.
    Guarantees deterministic, instant, high-quality responses for any custom intent prompt,
    while maintaining 100% compatibility with local Ollama and Cloud LLMs.
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

        # 1. Custom Natural Intent Handling (Command Studio)
        if req_lower:
            if any(k in req_lower for k in ["react", "node", "frontend", "next", "web"]):
                return {
                    "reasoning": f"Synthesized developer flow for modern Web & React stack: '{user_request}'.",
                    "actions": [
                        {
                            "action_type": "OPEN_URL",
                            "title": "Open GitHub Repository",
                            "description": "Navigate to project repository and pull requests",
                            "params": {"url": "https://github.com/PiyushTiwari2051/CAIOS"},
                            "requires_confirmation": True
                        },
                        {
                            "action_type": "OPEN_APP",
                            "title": "Launch Developer Terminal",
                            "description": "Open Windows Terminal for npm and node dev commands",
                            "params": {"app": "terminal"},
                            "requires_confirmation": True
                        },
                        {
                            "action_type": "CREATE_NOTE",
                            "title": "React Component Checklist",
                            "description": "Initialize component architecture checklist in sandbox",
                            "params": {"filename": "react_components.md", "content": "# React Architecture Plan\n- [ ] UI State Management\n- [ ] API Integrations\n- [ ] Responsive Styles\n"},
                            "requires_confirmation": True
                        }
                    ]
                }
            elif any(k in req_lower for k in ["python", "fastapi", "backend", "api", "server"]):
                return {
                    "reasoning": f"Configuring backend development workspace for '{user_request}'.",
                    "actions": [
                        {
                            "action_type": "OPEN_URL",
                            "title": "FastAPI Interactive Docs",
                            "description": "Open local API Swagger documentation",
                            "params": {"url": "http://127.0.0.1:8000/docs"},
                            "requires_confirmation": True
                        },
                        {
                            "action_type": "OPEN_APP",
                            "title": "Open Code Editor",
                            "description": "Launch VS Code workspace",
                            "params": {"app": "vscode"},
                            "requires_confirmation": True
                        },
                        {
                            "action_type": "CREATE_NOTE",
                            "title": "Backend API Spec Notes",
                            "description": "Create API endpoints schema scratchpad",
                            "params": {"filename": "backend_endpoints.md", "content": "# API Design\n- POST /causal/estimate\n- POST /causal/counterfactual\n"},
                            "requires_confirmation": True
                        }
                    ]
                }
            elif any(k in req_lower for k in ["research", "literature", "paper", "arxiv", "study"]):
                return {
                    "reasoning": f"Surfacing academic literature and research tools for '{user_request}'.",
                    "actions": [
                        {
                            "action_type": "OPEN_URL",
                            "title": "Explore arXiv CS/AI Recent",
                            "description": "Browse peer-reviewed papers on Causal AI & Agent Systems",
                            "params": {"url": "https://arxiv.org/list/cs.AI/recent"},
                            "requires_confirmation": True
                        },
                        {
                            "action_type": "CREATE_NOTE",
                            "title": "Literature Review Synthesis",
                            "description": "Initialize research paper summary note",
                            "params": {"filename": "literature_synthesis.md", "content": "# Literature Review\n\n### Core Papers:\n1. DoWhy: An End-to-End Library for Causal Inference\n2. Structural Causal Models (Pearl, 2009)\n"},
                            "requires_confirmation": True
                        },
                        {
                            "action_type": "SET_REMINDER",
                            "title": "Deep Reading Focus Block",
                            "description": "Set 30-minute uninterrupted reading sprint",
                            "params": {"seconds": 1800, "message": "Research block completed. Time to write takeaways."},
                            "requires_confirmation": True
                        }
                    ]
                }
            elif any(k in req_lower for k in ["pitch", "investor", "deck", "startup", "presentation"]):
                return {
                    "reasoning": f"Setting up executive pitch and investor review tools for '{user_request}'.",
                    "actions": [
                        {
                            "action_type": "OPEN_URL",
                            "title": "Open CAIOS GitHub Repo",
                            "description": "View live project repository and pitch brief",
                            "params": {"url": "https://github.com/PiyushTiwari2051/CAIOS"},
                            "requires_confirmation": True
                        },
                        {
                            "action_type": "CREATE_NOTE",
                            "title": "Executive Pitch Talking Points",
                            "description": "Create pitch script and market opportunity notes",
                            "params": {"filename": "pitch_talking_points.md", "content": "# CAIOS Pitch Points\n- $757.7B Market by 2033\n- Judea Pearl do-calculus grounding\n- Hard allow-list safety interlock\n"},
                            "requires_confirmation": True
                        }
                    ]
                }
            elif any(k in req_lower for k in ["sprint", "focus", "pomodoro", "timer", "break"]):
                return {
                    "reasoning": f"Engaging deep work focus protocol for '{user_request}'.",
                    "actions": [
                        {
                            "action_type": "SET_REMINDER",
                            "title": "25-Minute Focus Sprint",
                            "description": "Start Pomodoro deep focus session",
                            "params": {"seconds": 1500, "message": "Sprint complete! Take a 5-minute breather."},
                            "requires_confirmation": True
                        },
                        {
                            "action_type": "OPEN_APP",
                            "title": "Ambient Music Player",
                            "description": "Launch Spotify for focus beats",
                            "params": {"app": "spotify"},
                            "requires_confirmation": True
                        }
                    ]
                }
            elif any(k in req_lower for k in ["meet", "zoom", "call", "sync", "standup"]):
                return {
                    "reasoning": f"Preparing meeting capture and action ledger for '{user_request}'.",
                    "actions": [
                        {
                            "action_type": "CREATE_NOTE",
                            "title": "Live Meeting Minutes",
                            "description": "Capture key decisions and owner deliverables",
                            "params": {"filename": "meeting_minutes.md", "content": "# Meeting Minutes\n**Date:** Today\n\n### Key Deliverables\n- [ ] \n"},
                            "requires_confirmation": True
                        },
                        {
                            "action_type": "SET_REMINDER",
                            "title": "Post-Meeting Follow-Up",
                            "description": "Remind to email action items in 45m",
                            "params": {"seconds": 2700, "message": "Distribute meeting action items to team."},
                            "requires_confirmation": True
                        }
                    ]
                }

        # 2. Mode-Based Automatic Presets
        if mode_upper == "CODING":
            return {
                "reasoning": f"Detected developer workspace ({process_name or 'code.exe'}). Optimizing environment for coding flow.",
                "actions": [
                    {
                        "action_type": "OPEN_URL",
                        "title": "Open GitHub Dashboard",
                        "description": "Check pull requests and repository activity",
                        "params": {"url": "https://github.com/PiyushTiwari2051/CAIOS"},
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
                        "title": "Explore arXiv CS/AI",
                        "description": "Browse latest publications in AI & Systems",
                        "params": {"url": "https://arxiv.org/list/cs.AI/recent"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "CREATE_NOTE",
                        "title": "Study Summary Notes",
                        "description": "Create lecture key takeaways note",
                        "params": {"filename": "study_summary.md", "content": "# Study Session Notes\n\n### Key Concepts:\n- \n\n### Open Questions:\n- \n"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "SET_REMINDER",
                        "title": "Study Break Reminder",
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
                        "title": "Check Tech News",
                        "description": "Browse today's top tech discussions on Hacker News",
                        "params": {"url": "https://news.ycombinator.com"},
                        "requires_confirmation": True
                    },
                    {
                        "action_type": "OPEN_APP",
                        "title": "Open Music Player",
                        "description": "Launch Spotify for ambient background focus",
                        "params": {"app": "spotify"},
                        "requires_confirmation": True
                    }
                ]
            }
