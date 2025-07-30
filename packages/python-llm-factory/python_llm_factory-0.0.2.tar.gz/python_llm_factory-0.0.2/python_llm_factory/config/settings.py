from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()


class LLMProviderSettings(BaseSettings):
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    max_retries: int = 3


class OpenAISettings(LLMProviderSettings):
    api_key: str = os.getenv("OPENAI_API_KEY") or ""
    default_model: str = "gpt-4o"


class AnthropicSettings(LLMProviderSettings):
    api_key: str = os.getenv("ANTHROPIC_API_KEY") or ""
    default_model: str = "claude-3-5-sonnet-20240620"
    max_tokens: int = 1024


class GeminiSettings(LLMProviderSettings):
    api_key: str = os.getenv("GEMINI_API_KEY") or ""
    default_model: str = "gemini-1.5-flash"
    # default_model: str = "gemini-2.5-flash"
    max_tokens: int = 1024
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"


class LlamaSettings(LLMProviderSettings):
    api_key: str = "key"  # required, but not used
    default_model: str = "llama3"
    base_url: str = "http://localhost:11434/v1"


class Settings(BaseSettings):
    app_name: str = "GenAI Project Template"
    openai: OpenAISettings = OpenAISettings()
    anthropic: AnthropicSettings = AnthropicSettings()
    gemini: GeminiSettings = GeminiSettings()
    llama: LlamaSettings = LlamaSettings()


@lru_cache
def get_settings():
    return Settings()
