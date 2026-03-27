import requests
import json

class OllamaClient:
    def __init__(self, base_url: str = "http://host.docker.internal:11434", model: str = "llama3.1:8b"):
        self.base_url = base_url
        self.model = model

    def classify_error(self, error_log: str) -> dict:
        prompt = f"""
You are an Airflow task error classifier. Analyze the error and respond ONLY with JSON, no explanation.

Error:
{error_log}

Respond with exactly this JSON format:
{{
  "error_type": "rate_limit|network|auth|data_schema|unknown",
  "retry": true or false,
  "wait_seconds": <integer>,
  "reason": "<short explanation in English>"
}}
"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        raw = response.json()["response"]
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])