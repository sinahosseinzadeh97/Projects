"""LLM provider abstraction layer for PraticaAI.

Decouples the application from any specific LLM vendor (Gemini, OpenAI, Azure).
Swap providers by changing LLM_PROVIDER env variable.

# === FIX 2: Abstract the LLM layer (remove Gemini hard dependency) ===
"""

from __future__ import annotations

import os


class LLMProvider:
    """Abstract LLM provider. Swap Gemini for OpenAI/Azure
    by changing LLM_PROVIDER env variable.
    """

    PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # gemini | openai
    EXTRACTION_MODEL = os.getenv(
        "EXTRACTION_MODEL",
        "gemini-3-flash-preview",  # or "gpt-4o-mini"
    )
    VOICE_MODEL = os.getenv(
        "VOICE_MODEL",
        "gemini-3.1-flash-live-preview",  # or "gpt-4o-realtime"
    )

    @staticmethod
    def get_extraction_model() -> str:
        return LLMProvider.EXTRACTION_MODEL

    @staticmethod
    def get_voice_model() -> str:
        return LLMProvider.VOICE_MODEL

    @staticmethod
    def get_api_key() -> str:
        if LLMProvider.PROVIDER == "gemini":
            return os.getenv("GOOGLE_API_KEY", "")
        elif LLMProvider.PROVIDER == "openai":
            return os.getenv("OPENAI_API_KEY", "")
        raise ValueError(f"Unknown LLM provider: {LLMProvider.PROVIDER}")
