"""
Backend settings.

Read once at import from the environment, with `backend/.env` loaded first if
present. Everything has a working default so the service starts with no
configuration at all - that is the point of the seeded graph.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"


def _load_dotenv() -> None:
    """
    Minimal .env reader. python-dotenv is in requirements and used when
    available; this fallback keeps the service runnable if it is not, and
    never overwrites a variable already set in the real environment.
    """
    env_path = BACKEND_DIR / ".env"
    if not env_path.exists():
        return

    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


try:  # pragma: no cover - exercised by whichever branch is installed
    from dotenv import load_dotenv

    load_dotenv(BACKEND_DIR / ".env")
except ImportError:
    _load_dotenv()


def _flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    host: str = os.environ.get("HOST", "127.0.0.1")
    port: int = int(os.environ.get("PORT", "8000"))

    #: Origins allowed to call the API. The Next.js dev server is the default.
    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            origin.strip()
            for origin in os.environ.get(
                "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
            ).split(",")
            if origin.strip()
        )
    )

    # -- Cognee / LLM --------------------------------------------------------

    llm_api_key: str = os.environ.get("LLM_API_KEY", "")
    llm_provider: str = os.environ.get("LLM_PROVIDER", "gemini")
    llm_model: str = os.environ.get("LLM_MODEL", "gemini/gemini-3.6-flash")

    embedding_provider: str = os.environ.get("EMBEDDING_PROVIDER", "fastembed")
    embedding_model: str = os.environ.get(
        "EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"
    )
    embedding_dimensions: int = int(os.environ.get("EMBEDDING_DIMENSIONS", "384"))

    #: Master switch. Off means the service never imports or calls Cognee and
    #: answers are composed from retrieved evidence alone.
    use_cognee: bool = _flag("USE_COGNEE", True)

    #: Let the LLM phrase the `/ask` answer over retrieved evidence. Structured
    #: fields are always graph-derived regardless of this setting.
    use_llm_answers: bool = _flag("USE_LLM_ANSWERS", True)

    #: Seconds to wait on Cognee before falling back to the deterministic path.
    cognee_timeout_s: float = float(os.environ.get("COGNEE_TIMEOUT_S", "25"))

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_api_key)

    @property
    def cognee_enabled(self) -> bool:
        return self.use_cognee and self.llm_configured


settings = Settings()
