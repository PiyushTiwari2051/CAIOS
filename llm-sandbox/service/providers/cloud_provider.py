import os
import json
import httpx
import re
from typing import Dict, Any, Optional
from .base import BaseLLMProvider
from ..prompt_templates import SYSTEM_PROMPT, format_user_prompt

class GeminiCloudProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"

    async def generate_reasoning(
        self,
        mode: str,
        user_request: Optional[str] = None,
        active_window: Optional[str] = None,
        process_name: Optional[str] = None
    ) -> Dict[str, Any]:
        user_text = format_user_prompt(mode, user_request, active_window, process_name)
        payload = {
            "contents": [{
                "parts": [
                    {"text": f"{SYSTEM_PROMPT}\n\nContext:\n{user_text}\n\nOutput JSON:"}
                ]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(self.endpoint, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)

class OpenAICloudProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    async def generate_reasoning(
        self,
        mode: str,
        user_request: Optional[str] = None,
        active_window: Optional[str] = None,
        process_name: Optional[str] = None
    ) -> Dict[str, Any]:
        user_text = format_user_prompt(mode, user_request, active_window, process_name)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(self.endpoint, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            return json.loads(raw_text)
