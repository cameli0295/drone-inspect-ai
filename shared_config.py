"""Configuration partagée par les applications Streamlit et Flask."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Variable d'environnement obligatoire absente : {name}. "
            "Copiez .env.example vers .env puis renseignez-la."
        )
    return value.strip()


def _as_bool(value: object, *, default: bool = True) -> bool:
    """Convertit une option TOML/.env en booléen sans accepter d'ambiguïté."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Valeur booléenne invalide : {value!r}")


def _get_streamlit_mysql_config() -> dict[str, object] | None:
    """Lit ``st.secrets.mysql`` lorsqu'un contexte Streamlit le fournit."""
    try:
        import streamlit as st
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx(suppress_warning=True) is None:
            return None

        # En local, ne pas consulter st.secrets lorsqu'aucun fichier TOML
        # n'existe : Streamlit afficherait sinon un bandeau d'erreur rouge.
        # Sur Community Cloud, .env est absent et les secrets sont injectés
        # par la plateforme, donc st.secrets reste consulté normalement.
        secret_files = (
            BASE_DIR / ".streamlit" / "secrets.toml",
            Path.home() / ".streamlit" / "secrets.toml",
        )
        if (BASE_DIR / ".env").exists() and not any(
            path.exists() for path in secret_files
        ):
            return None

        section = st.secrets.get("mysql")
        if not section:
            return None
        return {
            "host": str(section["host"]).strip(),
            "port": int(section["port"]),
            "user": str(section["user"]).strip(),
            "password": str(section["password"]),
            "database": str(section["database"]).strip(),
            "charset": str(section.get("charset", "utf8mb4")).strip(),
            "use_unicode": _as_bool(section.get("use_unicode"), default=True),
        }
    except (FileNotFoundError, KeyError, RuntimeError, TypeError, ValueError):
        # Hors Streamlit ou sans secrets locaux : la configuration .env reste active.
        return None


def get_mysql_config() -> dict[str, object]:
    """Retourne la config Streamlit Cloud, sinon la configuration ``.env``."""
    streamlit_config = _get_streamlit_mysql_config()
    if streamlit_config is not None:
        return streamlit_config

    try:
        port = int(_required("MYSQL_PORT"))
    except ValueError as exc:
        raise RuntimeError("MYSQL_PORT doit être un entier.") from exc
    return {
        "host": _required("MYSQL_HOST"),
        "port": port,
        "user": _required("MYSQL_USER"),
        "password": _required("MYSQL_PASSWORD"),
        "database": _required("MYSQL_DATABASE"),
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4").strip(),
        "use_unicode": _as_bool(os.getenv("MYSQL_USE_UNICODE"), default=True),
    }
