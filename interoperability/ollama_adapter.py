import json
import os
from typing import Any, Dict, Optional
from urllib import error, request


class OllamaAgentAdapter:
    """Local LLM executor via Ollama HTTP API without silent mock fallback."""

    def __init__(
        self,
        model: Optional[str] = None,
        host: Optional[str] = None,
        timeout_sec: float = 15.0,
    ) -> None:
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama3.2")
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.timeout_sec = timeout_sec

    def execute(self, objective: str) -> Dict[str, Any]:
        url = f"{self.host}/api/generate"
        body = json.dumps(
            {
                "model": self.model,
                "prompt": f"Summarize this objective in one short sentence: {objective}",
                "stream": False,
            }
        ).encode("utf-8")
        req = request.Request(
            url=url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_sec) as resp:
                raw = resp.read().decode("utf-8")
                parsed = json.loads(raw)
                return {
                    "available": True,
                    "model": self.model,
                    "output": str(parsed.get("response", "")).strip(),
                }
        except (error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            return {
                "available": False,
                "model": self.model,
                "error": str(exc),
                "output": "",
            }
