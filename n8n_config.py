"""Configuración fail-closed para operaciones administrativas de n8n."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit


class ConfigError(ValueError):
    """La configuración no es segura o está incompleta."""


@dataclass(frozen=True)
class N8nConfig:
    api_url: str
    api_key: str = field(repr=False)
    workflow_dir: Path
    telegram_credential_id: str


def _required(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"Falta la variable obligatoria {name}")
    if "\n" in value or "\r" in value:
        raise ConfigError(f"{name} contiene saltos de línea")
    return value


def load_n8n_config(environ: Mapping[str, str] | None = None) -> N8nConfig:
    env = os.environ if environ is None else environ

    api_url = _required(env, "N8N_API_URL").rstrip("/")
    parsed = urlsplit(api_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ConfigError("N8N_API_URL debe usar HTTPS y contener un host")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ConfigError("N8N_API_URL no puede contener credenciales, query ni fragmento")
    if parsed.path.rstrip("/") != "/api/v1":
        raise ConfigError("N8N_API_URL debe terminar exactamente en /api/v1")

    api_key = _required(env, "N8N_API_KEY")
    if len(api_key) < 20:
        raise ConfigError("N8N_API_KEY es demasiado corta")

    workflow_dir = Path(
        env.get("N8N_WORKFLOW_DIR", str(Path(__file__).resolve().parent)),
    ).expanduser().resolve()
    if not workflow_dir.is_dir():
        raise ConfigError("N8N_WORKFLOW_DIR no existe o no es un directorio")

    return N8nConfig(
        api_url=api_url,
        api_key=api_key,
        workflow_dir=workflow_dir,
        telegram_credential_id=_required(env, "N8N_TELEGRAM_CREDENTIAL_ID"),
    )
