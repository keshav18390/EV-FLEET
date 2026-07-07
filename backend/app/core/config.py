"""
Central application configuration.
Loads from .env automatically via pydantic-settings.
Never crashes on missing keys -- downstream code checks `has_llm_key`.
"""
import logging
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        values[key.strip()] = raw_value.strip().strip('"').strip("'")
    return values


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM provider selection
    LLM_PROVIDER: str = "groq"  # openai | groq | openrouter | gemini | claude
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL_NAME: Optional[str] = None

    # Auth
    JWT_SECRET: str = "insecure-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "sqlite:///./fleet.db"

    # App
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000"

    # ---- Provider defaults (base_url, default model, key resolution) ----
    _PROVIDER_DEFAULTS = {
        "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
        "groq": {"base_url": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile"},
        "openrouter": {"base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-4o-mini"},
        "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "model": "gemini-1.5-flash"},
        "claude": {"base_url": "https://api.anthropic.com/v1", "model": "claude-3-5-sonnet-latest"},
    }

    @property
    def active_api_key(self) -> Optional[str]:
        provider = self.LLM_PROVIDER.lower()
        dotenv_config = _parse_dotenv(Path(".env"))
        dotenv_key_map = {
            "openai": dotenv_config.get("OPENAI_API_KEY"),
            "groq": dotenv_config.get("GROQ_API_KEY"),
            "openrouter": dotenv_config.get("OPENROUTER_API_KEY"),
            "gemini": dotenv_config.get("GEMINI_API_KEY"),
            "claude": dotenv_config.get("CLAUDE_API_KEY"),
        }
        dotenv_key = dotenv_key_map.get(provider)

        env_key_map = {
            "openai": self.OPENAI_API_KEY,
            "groq": self.GROQ_API_KEY,
            "openrouter": self.OPENROUTER_API_KEY,
            "gemini": self.GEMINI_API_KEY,
            "claude": self.CLAUDE_API_KEY,
        }
        env_key = env_key_map.get(provider)

        if dotenv_key and dotenv_key.strip():
            if env_key and env_key.strip() and env_key.strip() != dotenv_key.strip():
                logging.warning(
                    "LLM API key mismatch detected for provider '%s'. Using key from .env and ignoring OS environment override.",
                    provider,
                )
            return dotenv_key.strip()

        return env_key.strip() if env_key and env_key.strip() else None

    @property
    def has_llm_key(self) -> bool:
        key = self.active_api_key
        return bool(key and key.strip())

    @property
    def active_base_url(self) -> str:
        if self.LLM_BASE_URL:
            return self.LLM_BASE_URL
        defaults = self._PROVIDER_DEFAULTS.get(self.LLM_PROVIDER.lower(), self._PROVIDER_DEFAULTS["groq"])
        return defaults["base_url"]

    @property
    def active_model(self) -> str:
        if self.LLM_MODEL_NAME:
            return self.LLM_MODEL_NAME
        defaults = self._PROVIDER_DEFAULTS.get(self.LLM_PROVIDER.lower(), self._PROVIDER_DEFAULTS["groq"])
        return defaults["model"]


settings = Settings()
