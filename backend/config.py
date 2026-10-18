"""Configuration is loaded at app creation, never frozen at import time."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    api_key: str = ""
    cache_ttl: int = 300
    requests_per_minute: int = 10
    history_days: int = 730
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")

    @classmethod
    def from_env(cls):
        load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
        api_key = os.getenv("API_KEY", "").strip()
        if any(marker in api_key.lower() for marker in (
            "sua_chave", "your_key", "your_token", "cole_aqui", "exemplo"
        )):
            api_key = ""
        def number(name, default, low, high):
            value = int(os.getenv(name, str(default)))
            if not low <= value <= high:
                raise ValueError(f"{name} deve estar entre {low} e {high}.")
            return value
        return cls(
            api_key=api_key,
            cache_ttl=number("CACHE_TTL_SECONDS", 300, 0, 3600),
            requests_per_minute=number("API_REQUESTS_PER_MINUTE", 10, 1, 1000),
            history_days=number("HISTORY_DAYS", 730, 30, 3650),
            cors_origins=tuple(x.strip() for x in os.getenv(
                "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()),
        )

