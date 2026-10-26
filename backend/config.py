"""Configuration is loaded at app creation, never frozen at import time."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import dotenv_values

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"

@dataclass(frozen=True)
class Settings:
    api_key: str = ""
    cache_ttl: int = 300
    requests_per_minute: int = 10
    history_days: int = 730
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")

    on_vercel: bool = False
    environment: str = "local"
    client_requests_per_minute: int = 120

    @classmethod
    def from_env(cls):
        # Não alterar os.environ: uma nova leitura deve refletir o arquivo salvo.
        # Na Vercel, somente as variáveis do painel são utilizadas.
        on_vercel = os.getenv("VERCEL") == "1"
        values = {} if on_vercel else dotenv_values(ENV_FILE, encoding="utf-8-sig", interpolate=False)
        values.update(os.environ)
        def get(name, default=""):
            value = values.get(name)
            return default if value is None else value
        api_key = get("API_KEY").strip()
        if any(marker in api_key.lower() for marker in (
            "sua_chave", "your_key", "your_token", "cole_aqui", "exemplo"
        )):
            api_key = ""
        def number(name, default, low, high):
            try:
                value = int(get(name, str(default)))
            except ValueError:
                raise ValueError(f"{name} deve ser um número inteiro.") from None
            if not low <= value <= high:
                raise ValueError(f"{name} deve estar entre {low} e {high}.")
            return value
        # Deployments Vercel (inclusive Preview) usam configuração de produção.
        default_environment = "production" if on_vercel else "local"
        environment = get("APP_ENV", default_environment).strip().lower()
        if on_vercel and environment != "production":
            raise ValueError("Deployments Vercel exigem APP_ENV=production.")
        if environment not in {"local", "production"}:
            raise ValueError("APP_ENV deve ser local ou production.")
        if environment == "production" and not api_key:
            raise ValueError("Produção exige API_KEY configurada.")
        return cls(
            on_vercel=on_vercel,
            environment=environment,
            client_requests_per_minute=number("CLIENT_REQUESTS_PER_MINUTE", 120, 1, 10000),
            api_key=api_key,
            cache_ttl=number("CACHE_TTL_SECONDS", 300, 0, 3600),
            requests_per_minute=number("API_REQUESTS_PER_MINUTE", 10, 1, 1000),
            history_days=number("HISTORY_DAYS", 730, 30, 3650),
            cors_origins=tuple(x.strip() for x in get(
                "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()),
        )

