"""Application Flask parallèle à l'interface Streamlit."""

from __future__ import annotations

import os

from flask import Flask
from dotenv import load_dotenv

from shared_config import BASE_DIR


def create_app() -> Flask:
    load_dotenv(BASE_DIR / ".env")
    app = Flask(__name__)
    app.config.update(
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024,
        JSON_AS_ASCII=False,
    )

    from flask_app.routes import web

    app.register_blueprint(web)
    return app
