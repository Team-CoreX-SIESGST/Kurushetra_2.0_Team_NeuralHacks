import os
import base64
from typing import Optional, Dict, Any
import requests


class HFInferenceClient:
    """Minimal client for Hugging Face Inference API (hosted models)."""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"

    def _headers(self) -> Dict[str, str]:
        if not self.api_token:
            raise RuntimeError("HUGGINGFACE_API_TOKEN not configured")
        return {"Authorization": f"Bearer {self.api_token}"}

    def ocr_image(self, image_bytes: bytes, model: str = "microsoft/trocr-base-printed") -> Dict[str, Any]:
        """Call a hosted image-to-text model. Returns a simple dict with text or error."""
        url = f"{self.base_url}/{model}"
        try:
            response = requests.post(url, headers=self._headers(), data=image_bytes, timeout=60)
            response.raise_for_status()
            data = response.json()
            # TrOCR hosted usually returns a list with {"generated_text": "..."}
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return {"text": data[0]["generated_text"], "raw": data}
            # Some models may return a dict
            if isinstance(data, dict) and "generated_text" in data:
                return {"text": data["generated_text"], "raw": data}
            return {"text": "", "raw": data}
        except Exception as e:
            return {"error": str(e)}

    def summarize_text(
        self,
        text: str,
        model: str = "facebook/bart-large-cnn",
        max_length: int = 256,
        min_length: int = 64,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Call a hosted summarization model. Returns dict with summary or error."""
        url = f"{self.base_url}/{model}"
        payload: Dict[str, Any] = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": temperature is not None,
            },
            "options": {"wait_for_model": True},
        }
        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            # Expected format: list of {"summary_text": "..."}
            if isinstance(data, list) and data and "summary_text" in data[0]:
                return {"summary": data[0]["summary_text"], "raw": data}
            if isinstance(data, dict) and "summary_text" in data:
                return {"summary": data["summary_text"], "raw": data}
            return {"summary": "", "raw": data}
        except Exception as e:
            return {"error": str(e)}


