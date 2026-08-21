import json
import httpx
import re
from typing import Dict, Any, Optional
from .base import BaseLLMProvider
from ..prompt_templates import SYSTEM_PROMPT, format_user_prompt

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen3:4b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def _resolve_active_model(self, client: httpx.AsyncClient) -> str:
        """Verifies if the specified model is available, or resolves the first active model."""
        try:
            resp = await client.get(f"{self.base_url}/api/tags", timeout=3.0)
            if resp.status_code == 200:
                models = [m.get("name") for m in resp.json().get("models", [])]
                if self.model in models:
                    return self.model
                for m in models:
                    if self.model.split(":")[0] in m:
                        return m
                if models:
                    return models[0]
        except Exception:
            pass
        return self.model

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Robustly extracts JSON from raw LLM output, handling markdown fences and conversational prefixes."""
        text = text.strip()
        # 1. Direct parse attempt
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Strip ```json ... ``` code blocks
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 3. Search for outermost curly braces
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            substring = text[start:end+1]
            try:
                return json.loads(substring)
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not parse valid JSON from LLM output: {text[:200]}")

    async def generate_reasoning(
        self,
        mode: str,
        user_request: Optional[str] = None,
        active_window: Optional[str] = None,
        process_name: Optional[str] = None
    ) -> Dict[str, Any]:
        prompt = format_user_prompt(mode, user_request, active_window, process_name)

        async with httpx.AsyncClient(timeout=90.0) as client:
            active_model = await self._resolve_active_model(client)
            
            payload = {
                "model": active_model,
                "prompt": f"{SYSTEM_PROMPT}\n\nUser Context:\n{prompt}\n\nReturn strictly valid JSON only:",
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "num_predict": 512
                }
            }

            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            result = resp.json()
            raw_text = result.get("response", "{}")
            
            return self._extract_json(raw_text)
