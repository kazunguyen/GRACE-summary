"""
GRACE Multi-Provider LLM Backbone Engine
Supports:
  1. FPT Cloud / OpenAI-Compatible API (with explicit thinking=False)
  2. Google Vertex AI (GenAI SDK)
  3. Deterministic Mock LLM (for instant offline testing & verification)

Enforces contract parameters:
  - Temperature: 0.0
  - Seed: 42
  - Max output tokens: 256
  - Thinking mode disabled to preserve token budget for binary answer
  - 5-attempt exponential backoff retry policy
"""

from __future__ import annotations

import json
import logging
import time
import urllib.request
from typing import Dict, Any, Optional
from config import config

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified client handling API communication across providers."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        use_mock: bool = False,
    ):
        self.use_mock = use_mock or config.use_mock
        self.provider = provider or config.provider
        self.model_name = model_name or config.model_name
        self.temperature = config.temperature
        self.seed = config.random_seed
        self.max_tokens = config.max_tokens
        self.thinking_enabled = config.thinking_enabled

        # FPT & OpenAI configs
        self.fpt_api_key = config.env_vars.get("FPT_API", "")
        self.fpt_base_url = config.env_vars.get("FPT_BASE_URL", "https://token-api.fpt.ai/v1")
        if not self.fpt_base_url.endswith("/v1"):
            self.fpt_base_url = self.fpt_base_url.rstrip("/") + "/v1"

        if not self.use_mock:
            if not self.fpt_api_key and "VERTEX_PROJECT" not in config.env_vars:
                logger.warning("No API credentials found (FPT_API or VERTEX_PROJECT). Falling back to Mock LLM.")
                self.use_mock = True

    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Execute generation with exponential backoff retry policy.
        Returns: {
            "raw_response": str,
            "request_status": "ok" | "invalid_exhausted",
            "request_error": Optional[str],
            "attempts": int,
            "model": str,
        }
        """
        if self.use_mock:
            return self._mock_generate(prompt)

        attempts = config.retry_max_attempts
        delay = config.retry_delay_base
        max_delay = config.retry_delay_max
        last_error = None
        raw_text = ""

        for attempt in range(1, attempts + 1):
            try:
                raw_text = self._call_provider(prompt)
                return {
                    "raw_response": raw_text,
                    "request_status": "ok",
                    "request_error": None,
                    "attempts": attempt,
                    "model": self.model_name,
                }
            except Exception as e:
                last_error = repr(e)
                logger.warning("Attempt %d/%d failed: %s", attempt, attempts, last_error)
                if attempt < attempts:
                    sleep_time = min(max_delay, delay * (2 ** (attempt - 1)))
                    time.sleep(sleep_time)

        return {
            "raw_response": "",
            "request_status": "invalid_exhausted",
            "request_error": last_error,
            "attempts": attempts,
            "model": self.model_name,
        }

    def _call_provider(self, prompt: str) -> str:
        """Dispatch call to provider."""
        if self.fpt_api_key:
            return self._call_fpt_openai(prompt)
        return self._call_vertex_ai(prompt)

    def _call_fpt_openai(self, prompt: str) -> str:
        """Call FPT Cloud / OpenAI-compatible endpoint."""
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "seed": self.seed,
            "max_tokens": self.max_tokens,
            "stream": False,
        }

        # EXPLICITLY DISABLE THINKING TO PREVENT EXHAUSTING MAX_TOKENS BUDGET
        model_lower = self.model_name.lower()
        if "deepseek" in model_lower:
            payload["chat_template_kwargs"] = {"thinking": False}
        elif "qwen" in model_lower:
            payload["chat_template_kwargs"] = {"enable_thinking": False}

        req = urllib.request.Request(
            f"{self.fpt_base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.fpt_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.load(resp)

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"FPT API returned no choices: {data}")

        msg = choices[0].get("message", {})
        content = msg.get("content") or ""
        if not content and "reasoning_content" in msg:
            content = msg["reasoning_content"]

        return content.strip()

    def _call_vertex_ai(self, prompt: str) -> str:
        """Call Google Vertex AI GenAI SDK."""
        from google import genai
        from google.genai import types

        project = config.env_vars.get("VERTEX_PROJECT")
        location = config.env_vars.get("VERTEX_LOCATION", "us-central1")
        client = genai.Client(vertexai=True, project=project, location=location)

        gen_config = types.GenerateContentConfig(
            temperature=self.temperature,
            seed=self.seed,
            max_output_tokens=self.max_tokens,
        )

        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=gen_config,
        )
        return response.text or ""

    def _mock_generate(self, prompt: str) -> Dict[str, Any]:
        """
        Deterministic Mock LLM for verification & tests without network calls.
        Detects security-sensitive patterns or returns 0/1 reliably.
        """
        prompt_lower = prompt.lower()
        is_vuln = any(kw in prompt_lower for kw in ["strcpy", "gets", "sprintf", "buffer overflow", "bad_"])
        pred = "1" if is_vuln else "0"
        return {
            "raw_response": pred,
            "request_status": "ok",
            "request_error": None,
            "attempts": 1,
            "model": "mock-llm-engine",
        }
