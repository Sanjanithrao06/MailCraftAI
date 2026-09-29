import logging
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

OPENAI_MODELS = {"primary": "gpt-4o", "baseline": "gpt-4o-mini", "judge": "gpt-4o"}
GROQ_MODELS = {
    "primary": "openai/gpt-oss-120b",
    "baseline": "openai/gpt-oss-20b",
    "judge": "openai/gpt-oss-120b",
}


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", description="OpenAI API key")
    groq_api_key: str = Field(default="", description="Groq API key")

    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2024-08-01-preview"

    provider: str = Field(default="auto", description="LLM provider: auto, openai, groq, or azure")
    primary_model: str = ""
    baseline_model: str = ""
    judge_model: str = ""

    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def resolved_provider(self) -> str:
        """Auto-detect provider from available API keys if set to 'auto'."""
        if self.provider != "auto":
            return self.provider
        if self.openai_api_key and self.openai_api_key.startswith("sk-"):
            return "openai"
        if self.azure_openai_api_key and self.azure_openai_endpoint:
            return "azure"
        if self.groq_api_key:
            return "groq"
        return "openai"

    @property
    def use_azure(self) -> bool:
        return self.resolved_provider == "azure"

    @property
    def use_groq(self) -> bool:
        return self.resolved_provider == "groq"

    @property
    def has_valid_key(self) -> bool:
        """Check if at least one API key is configured (non-empty, non-dummy)."""
        if self.openai_api_key and self.openai_api_key.startswith("sk-") and "test" not in self.openai_api_key:
            return True
        if self.groq_api_key and self.groq_api_key.startswith("gsk_"):
            return True
        if self.azure_openai_api_key and self.azure_openai_endpoint:
            return True
        return False

    def get_model_name(self, role: str) -> str:
        """Return the model name for a role (primary/baseline/judge).
        If explicitly set in .env, use that. Otherwise pick defaults for the provider."""
        explicit = getattr(self, f"{role}_model", "")
        if explicit:
            return explicit
        defaults = OPENAI_MODELS if not self.use_groq else GROQ_MODELS
        return defaults.get(role, defaults["primary"])


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    logger.info("Provider auto-detected: %s", s.resolved_provider)
    return s


def reset_settings() -> Settings:
    """Clear cached settings and reload from .env. Useful for testing."""
    get_settings.cache_clear()
    return get_settings()
