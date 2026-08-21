from typing import Optional, Dict, Tuple, List
from ..models.mode import ModeEnum, ModeClassification
from ..models.context import ContextPayload

# Process and window title heuristic mappings
PROCESS_RULES: Dict[str, Tuple[ModeEnum, float, str]] = {
    # Coding
    "code.exe": (ModeEnum.CODING, 0.98, "Active IDE detected: Visual Studio Code"),
    "code": (ModeEnum.CODING, 0.98, "Active IDE detected: VS Code"),
    "cursor.exe": (ModeEnum.CODING, 0.98, "Active IDE detected: Cursor Editor"),
    "cursor": (ModeEnum.CODING, 0.98, "Active IDE detected: Cursor Editor"),
    "pycharm64.exe": (ModeEnum.CODING, 0.95, "Active IDE detected: PyCharm"),
    "devenv.exe": (ModeEnum.CODING, 0.95, "Active IDE detected: Visual Studio"),
    "windowsterminal.exe": (ModeEnum.CODING, 0.85, "Terminal environment active"),
    "powershell.exe": (ModeEnum.CODING, 0.80, "Command shell active"),
    "cmd.exe": (ModeEnum.CODING, 0.75, "Command prompt active"),
    
    # Writing & Documentation
    "winword.exe": (ModeEnum.WRITING, 0.95, "Word processor active: Microsoft Word"),
    "notepad.exe": (ModeEnum.WRITING, 0.90, "Text editor active: Notepad"),
    "notepad++.exe": (ModeEnum.WRITING, 0.85, "Text editor active: Notepad++"),
    "notion.exe": (ModeEnum.WRITING, 0.90, "Note workspace active: Notion"),
    "obsidian.exe": (ModeEnum.WRITING, 0.92, "Knowledge workspace active: Obsidian"),
    "typora.exe": (ModeEnum.WRITING, 0.95, "Markdown editor active: Typora"),
    
    # Meeting & Communication
    "teams.exe": (ModeEnum.MEETING, 0.95, "Collaboration client active: MS Teams"),
    "zoom.exe": (ModeEnum.MEETING, 0.98, "Video conferencing active: Zoom"),
    "slack.exe": (ModeEnum.MEETING, 0.85, "Team chat active: Slack"),
    "discord.exe": (ModeEnum.MEETING, 0.80, "Voice/chat client active: Discord"),
    
    # Studying & Research
    "acrobat.exe": (ModeEnum.STUDYING, 0.90, "PDF reader active: Adobe Acrobat"),
    "acrord32.exe": (ModeEnum.STUDYING, 0.90, "PDF reader active: Adobe Reader"),
    "foxitreader.exe": (ModeEnum.STUDYING, 0.90, "PDF reader active: Foxit Reader"),
    "zotero.exe": (ModeEnum.STUDYING, 0.95, "Reference manager active: Zotero"),
    "kindle.exe": (ModeEnum.STUDYING, 0.92, "E-reader active: Kindle"),
}

KEYWORD_RULES: List[Tuple[str, ModeEnum, float, str]] = [
    # Meeting keywords in titles
    ("zoom meeting", ModeEnum.MEETING, 0.95, "Meeting detected in window title"),
    ("google meet", ModeEnum.MEETING, 0.95, "Google Meet active in browser"),
    ("microsoft teams", ModeEnum.MEETING, 0.90, "Teams call active in window title"),
    ("webex", ModeEnum.MEETING, 0.90, "Webex call detected"),
    
    # Coding keywords
    ("github", ModeEnum.CODING, 0.88, "Browsing GitHub repository"),
    ("gitlab", ModeEnum.CODING, 0.88, "Browsing GitLab repository"),
    ("stack overflow", ModeEnum.CODING, 0.85, "Viewing developer Q&A on Stack Overflow"),
    ("localhost:", ModeEnum.CODING, 0.85, "Testing local development server"),
    (".py", ModeEnum.CODING, 0.90, "Python source file active"),
    (".ts", ModeEnum.CODING, 0.90, "TypeScript source file active"),
    (".js", ModeEnum.CODING, 0.90, "JavaScript source file active"),
    (".cpp", ModeEnum.CODING, 0.90, "C++ source file active"),
    (".rs", ModeEnum.CODING, 0.90, "Rust source file active"),
    
    # Studying & Research
    ("arxiv", ModeEnum.STUDYING, 0.92, "Reading research papers on arXiv"),
    ("google scholar", ModeEnum.STUDYING, 0.90, "Researching on Google Scholar"),
    ("coursera", ModeEnum.STUDYING, 0.90, "Online course lecture active"),
    ("edx", ModeEnum.STUDYING, 0.90, "Online course lecture active"),
    ("wikipedia", ModeEnum.STUDYING, 0.80, "Reading reference encyclopedia"),
    ("pdf", ModeEnum.STUDYING, 0.82, "Document reading mode active"),
    
    # Writing
    ("google docs", ModeEnum.WRITING, 0.92, "Document editing in Google Docs"),
    ("overleaf", ModeEnum.WRITING, 0.95, "LaTeX authoring in Overleaf"),
    ("medium.com", ModeEnum.WRITING, 0.80, "Article publishing/reading"),
]

DEFAULT_MODE_ASSETS = {
    ModeEnum.CODING: {
        "suggested_apps": ["vscode", "terminal", "browser"],
        "suggested_shortcuts": ["Open GitHub", "Dev Docs", "Open Terminal", "Quick Scratchpad Note"]
    },
    ModeEnum.WRITING: {
        "suggested_apps": ["notepad", "obsidian", "word"],
        "suggested_shortcuts": ["Create Meeting Notes", "Dictionary", "Open Outline", "Focus Timer"]
    },
    ModeEnum.STUDYING: {
        "suggested_apps": ["browser", "notepad", "calculator"],
        "suggested_shortcuts": ["ArXiv Search", "Wikipedia Lookup", "Study Timer (25m)", "Flashcards"]
    },
    ModeEnum.MEETING: {
        "suggested_apps": ["notepad", "slack", "teams"],
        "suggested_shortcuts": ["Mute All / Do Not Disturb", "Open Meeting Agenda", "Quick Action Items Note", "Follow-up Reminder"]
    },
    ModeEnum.IDLE: {
        "suggested_apps": ["browser", "spotify"],
        "suggested_shortcuts": ["Resume Last Workspace", "Check Reminders", "Daily Overview"]
    }
}

class ModeClassifier:
    """Classifies user mode deterministically from lightweight process/title signals."""
    
    def classify(self, context: ContextPayload, manual_override: Optional[ModeEnum] = None) -> ModeClassification:
        # 1. Check manual override first
        if manual_override is not None:
            assets = DEFAULT_MODE_ASSETS.get(manual_override, DEFAULT_MODE_ASSETS[ModeEnum.IDLE])
            return ModeClassification(
                mode=manual_override,
                confidence=1.0,
                reasoning="Manual mode override selected by user",
                is_manual_override=True,
                suggested_apps=assets["suggested_apps"],
                suggested_shortcuts=assets["suggested_shortcuts"]
            )
            
        proc = (context.process_name or "").lower().strip()
        title = (context.window_title or "").lower().strip()
        
        # 2. Window Title Rules (Higher specificity for browser tabs)
        for keyword, mode, conf, reason in KEYWORD_RULES:
            if keyword in title:
                assets = DEFAULT_MODE_ASSETS[mode]
                return ModeClassification(
                    mode=mode,
                    confidence=conf,
                    reasoning=f"{reason} (matched '{keyword}')",
                    is_manual_override=False,
                    suggested_apps=assets["suggested_apps"],
                    suggested_shortcuts=assets["suggested_shortcuts"]
                )
                
        # 3. Process Name Rules
        if proc in PROCESS_RULES:
            mode, conf, reason = PROCESS_RULES[proc]
            assets = DEFAULT_MODE_ASSETS[mode]
            return ModeClassification(
                mode=mode,
                confidence=conf,
                reasoning=reason,
                is_manual_override=False,
                suggested_apps=assets["suggested_apps"],
                suggested_shortcuts=assets["suggested_shortcuts"]
            )
            
        # 4. Browser default heuristics
        if any(b in proc for b in ["chrome", "msedge", "firefox", "brave", "opera", "safari"]):
            mode = ModeEnum.STUDYING
            assets = DEFAULT_MODE_ASSETS[mode]
            return ModeClassification(
                mode=mode,
                confidence=0.65,
                reasoning=f"Web browser active: {proc}",
                is_manual_override=False,
                suggested_apps=assets["suggested_apps"],
                suggested_shortcuts=assets["suggested_shortcuts"]
            )
            
        # 5. Fallback: IDLE / Ambient
        mode = ModeEnum.IDLE
        assets = DEFAULT_MODE_ASSETS[mode]
        return ModeClassification(
            mode=mode,
            confidence=0.5,
            reasoning=f"Ambient context (Process: {proc or 'none'})",
            is_manual_override=False,
            suggested_apps=assets["suggested_apps"],
            suggested_shortcuts=assets["suggested_shortcuts"]
        )

classifier = ModeClassifier()
