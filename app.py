"""
DroneInspect AI — version professionnelle corrigée.
Les KPI, pipelines et cartes utilisent des composants Streamlit natifs
pour éviter l’affichage brut de code HTML.

DroneInspect AI - Application Streamlit complète
================================================

Fonctionnalités principales
---------------------------
- Authentification locale simple avec rôles (Administrateur, Inspecteur, Observateur)
- Connexion MySQL locale configurée par variables d'environnement
- Création et historique des missions d'inspection
- Pipeline automatique à deux niveaux :
    1) MobileNetV2 : Crack / No Crack
    2) EfficientNetB3 : classification multi-label des défauts si une fissure est détectée
- Enregistrement transactionnel dans MySQL : images, prédictions, rapports et logs
- Historique métier avec jointures SQL
- Génération et téléchargement de rapports PDF
- Dashboard Plotly
- Administration : utilisateurs, modèles et logs

Lancement
---------
streamlit run DroneInspect_AI_FINAL.py

Dépendances
-----------
pip install streamlit mysql-connector-python pandas pillow tensorflow numpy plotly reportlab openpyxl
"""

from __future__ import annotations

import hashlib
import io
import os
import time
import zipfile
from importlib import import_module
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from shared_config import get_mysql_config

render_import_page = import_module(
    "6_Import_Referentiel"
).render_import_page
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.models import load_model

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "Le paquet mysql-connector-python est absent. "
        "Installe-le avec : pip install mysql-connector-python"
    ) from exc

try:
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Image as RLImage,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib import colors

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# -----------------------------------------------------------------------------
# CONFIGURATION GÉNÉRALE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="DroneInspect AI",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cache le menu automatique créé par un éventuel dossier `pages/`.
# Le menu métier personnalisé reste visible.
st.markdown(
    """
    <style>
        :root {
            --primary: #0F4C81;
            --primary-dark: #0B3559;
            --secondary: #1F8A70;
            --accent: #F59E0B;
            --danger: #D62828;
            --surface: #FFFFFF;
            --surface-soft: #F5F8FC;
            --border: #D9E3EF;
            --text: #1F2937;
            --muted: #6B7280;
        }

        [data-testid="stSidebarNav"] {
            display: none;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top right, rgba(15, 76, 129, 0.08), transparent 28%),
                linear-gradient(180deg, #F8FBFF 0%, #F2F6FB 100%);
        }

        [data-testid="stHeader"] {
            background: rgba(248, 251, 255, 0.75);
            backdrop-filter: blur(10px);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0B3559 0%, #0F4C81 100%);
            border-right: 1px solid rgba(255,255,255,0.12);
        }

        [data-testid="stSidebar"] * {
            color: #F8FAFC;
        }

        [data-testid="stSidebar"] .stRadio label {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 0.55rem 0.75rem;
            margin-bottom: 0.35rem;
            transition: all 0.2s ease;
        }

        [data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(255,255,255,0.12);
            transform: translateX(3px);
        }

        .block-container {
            max-width: 1450px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            color: var(--text);
            letter-spacing: -0.02em;
        }

        .app-hero {
            background: linear-gradient(135deg, #0B3559 0%, #0F4C81 58%, #1F8A70 100%);
            border-radius: 22px;
            padding: 2.2rem 2.4rem;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 18px 45px rgba(15, 76, 129, 0.20);
        }

        .app-hero h1 {
            color: white;
            margin: 0;
            font-size: 2.35rem;
        }

        .app-hero p {
            color: rgba(255,255,255,0.88);
            font-size: 1.05rem;
            margin: 0.55rem 0 0;
            max-width: 900px;
        }

        .status-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
            margin-top: 1.2rem;
        }

        .status-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: rgba(255,255,255,0.13);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            font-size: 0.9rem;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--text);
            margin: 1.2rem 0 0.8rem;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .kpi-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem 1.1rem;
            box-shadow: 0 8px 24px rgba(31, 41, 55, 0.06);
        }

        .kpi-label {
            color: var(--muted);
            font-size: 0.88rem;
            margin-bottom: 0.35rem;
        }

        .kpi-value {
            font-size: 1.9rem;
            font-weight: 800;
            color: var(--primary-dark);
        }

        .kpi-sub {
            color: var(--muted);
            font-size: 0.8rem;
            margin-top: 0.25rem;
        }

        .content-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 10px 30px rgba(31, 41, 55, 0.06);
            margin-bottom: 1rem;
        }

        .pipeline {
            display: grid;
            grid-template-columns: 1fr auto 1fr auto 1fr;
            gap: 0.75rem;
            align-items: center;
            margin-top: 0.75rem;
        }

        .pipeline-step {
            background: #F7FAFD;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.9rem;
            text-align: center;
            min-height: 92px;
        }

        .pipeline-arrow {
            color: var(--primary);
            font-size: 1.4rem;
            font-weight: 800;
        }

        .badge {
            display: inline-block;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-weight: 700;
            font-size: 0.85rem;
        }

        .badge-faible {
            background: #DCFCE7;
            color: #166534;
        }

        .badge-moyenne {
            background: #FEF3C7;
            color: #92400E;
        }

        .badge-elevee {
            background: #FFEDD5;
            color: #9A3412;
        }

        .badge-critique {
            background: #FEE2E2;
            color: #991B1B;
        }

        .result-card {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
            border: 1px solid var(--border);
            border-left: 5px solid var(--primary);
            border-radius: 16px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 8px 24px rgba(31, 41, 55, 0.06);
        }

        .small-note {
            font-size: 0.88rem;
            color: var(--muted);
        }

        .inspection-info-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin: 0.5rem 0 1.25rem;
        }

        .inspection-info-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.9rem 1rem;
            min-width: 0;
            box-shadow: 0 8px 24px rgba(31,41,55,0.05);
        }

        .inspection-info-label {
            color: var(--muted);
            font-size: 0.82rem;
            margin-bottom: 0.35rem;
        }

        .inspection-info-value {
            color: var(--text);
            font-size: 1.05rem;
            font-weight: 600;
            line-height: 1.3;
            overflow-wrap: anywhere;
        }

        .analysis-form-heading {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1.25rem;
        }

        .analysis-form-heading h2 {
            margin: 0;
            color: var(--primary-dark);
            font-size: 1.65rem;
        }

        .analysis-form-heading p {
            margin: 0.35rem 0 0;
            color: var(--muted);
        }

        .analysis-step-badge {
            background: #EAF3FB;
            color: var(--primary);
            border-radius: 999px;
            padding: 0.4rem 0.75rem;
            font-size: 0.78rem;
            font-weight: 800;
            white-space: nowrap;
        }

        div[data-testid="stFileUploaderDropzone"] {
            min-height: 180px;
            border: 2px dashed #9FB7CF;
            border-radius: 16px;
            background: #F7FAFF;
        }

        div[data-testid="stFileUploaderDropzone"]:hover {
            border-color: var(--primary);
            background: #F0F7FD;
        }

        div[data-testid="stFileUploaderDropzone"] button {
            border: 1px solid #B8C8D9;
            background: white;
            color: var(--primary-dark);
        }

        @media (max-width: 900px) {
            .inspection-info-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 1rem;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(31,41,55,0.05);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 12px;
            border: none;
            min-height: 44px;
            font-weight: 700;
            box-shadow: 0 6px 16px rgba(15, 76, 129, 0.15);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0F4C81, #1F8A70);
        }

        @media (max-width: 1000px) {
            .kpi-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .pipeline {
                grid-template-columns: 1fr;
            }

            .pipeline-arrow {
                transform: rotate(90deg);
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_hero(title: str, subtitle: str, chips: Optional[List[str]] = None) -> None:
    """Affiche une bannière professionnelle réutilisable."""
    chip_html = ""
    if chips:
        chip_html = '<div class="status-row">' + "".join(
            f'<span class="status-chip">● {chip}</span>' for chip in chips
        ) + "</div>"

    st.markdown(
        f"""
        <div class="app-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            {chip_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(items: List[Tuple[str, Any, str]]) -> None:
    """
    Affiche les indicateurs avec les composants Streamlit natifs.

    Cette méthode évite l'affichage brut des balises HTML sur certaines
    versions de Streamlit.
    """
    if not items:
        return

    for start_index in range(0, len(items), 4):
        current_items = items[start_index:start_index + 4]
        columns = st.columns(len(current_items))

        for column, (label, value, subtext) in zip(columns, current_items):
            with column:
                st.metric(
                    label=label,
                    value=value,
                    help=subtext,
                )
                st.caption(subtext)


def priority_badge(priority: str) -> str:
    """Renvoie un badge HTML correspondant au niveau de priorité."""
    normalized = (priority or "").strip().lower()
    css_class = {
        "faible": "badge-faible",
        "moyenne": "badge-moyenne",
        "élevée": "badge-elevee",
        "elevee": "badge-elevee",
        "critique": "badge-critique",
    }.get(normalized, "badge-moyenne")

    return f'<span class="badge {css_class}">{priority}</span>'


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
MODEL_DIR = BASE_DIR / "models"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MOBILENET_MODEL_PATH = MODEL_DIR / "MobileNetV2_archive_structure_commente.keras"
EFFICIENTNET_MODEL_PATH = MODEL_DIR / "efficientnetb3_concrete_defects_corrige.keras"

# Seuil du niveau 1. Le niveau 2 est lancé automatiquement si Crack est détecté.
MOBILENET_CRACK_THRESHOLD = 0.50

# Ordre de sortie du modèle CODEBRIM déployé.
# IMPORTANT : cet ordre doit rester identique à celui utilisé à l'entraînement.
CODEBRIM_LABELS = [
    "Background",
    "Crack",
    "Spallation",
    "Efflorescence",
    "ExposedBars",
    "CorrosionStain",
]

CODEBRIM_THRESHOLDS = {
    "Background": 0.55,
    "Crack": 0.55,
    "Spallation": 0.60,
    "Efflorescence": 0.30,
    "ExposedBars": 0.65,
    "CorrosionStain": 0.35,
}

# Correspondance entre les sorties du modèle et les classes présentes dans MySQL.
# Honeycombing reste dans la base mais n'est pas produit par ce modèle précis.
CODEBRIM_CLASS_MAPPING = {
    "Background": {
        "db_name": "No Crack",
        "priority": "Faible",
        "recommendation": "Aucun défaut structurel significatif détecté.",
    },
    "Crack": {
        "db_name": "Crack",
        "priority": "Moyenne",
        "recommendation": (
            "Programmer une inspection de contrôle afin de surveiller "
            "l'évolution de la fissure."
        ),
    },
    "Spallation": {
        "db_name": "Spallation",
        "priority": "Critique",
        "recommendation": (
            "Sécuriser la zone et programmer rapidement une réparation "
            "du béton détérioré."
        ),
    },
    "Efflorescence": {
        "db_name": "Efflorescence",
        "priority": "Faible",
        "recommendation": (
            "Contrôler l'origine de l'humidité et surveiller l'évolution "
            "des dépôts."
        ),
    },
    "ExposedBars": {
        "db_name": "Exposed Rebar",
        "priority": "Critique",
        "recommendation": (
            "Réaliser une inspection structurelle urgente des armatures "
            "métalliques apparentes."
        ),
    },
    "CorrosionStain": {
        "db_name": "Corrosion",
        "priority": "Élevée",
        "recommendation": (
            "Prévoir rapidement un diagnostic et un traitement anticorrosion."
        ),
    },
}


# -----------------------------------------------------------------------------
# CONNEXION MYSQL
# -----------------------------------------------------------------------------
MYSQL_CONFIG = get_mysql_config()


def get_connection():
    """
    Ouvre une connexion à la base locale MySQL.

    Les paramètres sont chargés depuis le fichier ``.env`` local.
    """
    return mysql.connector.connect(
        **MYSQL_CONFIG,
        autocommit=False,
    )


@contextmanager
def mysql_transaction():
    """
    Encapsule plusieurs écritures dans une transaction atomique.

    - commit si toutes les opérations réussissent ;
    - rollback automatique en cas d'erreur ;
    - fermeture garantie du curseur et de la connexion.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            cursor.close()
        finally:
            conn.close()


def read_dataframe(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> pd.DataFrame:
    """Exécute une requête SELECT et renvoie le résultat sous forme de DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()


def fetch_one_value(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> Any:
    """Renvoie la première colonne de la première ligne d'une requête."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        conn.close()


def is_valid_sha256(value: Optional[str]) -> bool:
    """Vérifie qu'une chaîne est un hash SHA-256 hexadécimal de 64 caractères."""
    if not value or len(value) != 64:
        return False
    return all(character in "0123456789abcdefABCDEF" for character in value)


def verify_admin_password(email: str, password: str) -> bool:
    """Vérifie les identifiants d'un compte administrateur actif."""
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    stored_hash = fetch_one_value(
        """
        SELECT password_hash
        FROM users
        WHERE email = %s
          AND role = 'Administrateur'
          AND is_active = 1
        """,
        (email.strip().lower(),),
    )
    return bool(stored_hash) and stored_hash == password_hash


def ensure_database_compatibility() -> None:
    """
    Met la table users au format attendu par l'application.

    Cette migration est idempotente :
    elle peut être exécutée à chaque démarrage sans dupliquer les colonnes.
    """
    with mysql_transaction() as (_, cursor):
        cursor.execute("SHOW COLUMNS FROM users LIKE 'password_hash'")
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE users "
                "ADD COLUMN password_hash VARCHAR(64) NULL AFTER email"
            )

        cursor.execute("SHOW COLUMNS FROM users LIKE 'is_active'")
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE users "
                "ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"
            )


def get_id_by_name(
    table: str,
    id_column: str,
    name_column: str,
    name: str,
) -> int:
    """
    Récupère dynamiquement un identifiant.

    La liste blanche empêche l'injection de noms de tables ou de colonnes.
    """
    allowed = {
        ("models", "model_id", "model_name"),
        ("datasets", "dataset_id", "dataset_name"),
        ("defect_classes", "class_id", "class_name"),
    }

    if (table, id_column, name_column) not in allowed:
        raise ValueError("Table ou colonnes non autorisées.")

    value = fetch_one_value(
        f"SELECT {id_column} "
        f"FROM {table} "
        f"WHERE {name_column} = %s "
        f"LIMIT 1",
        (name,),
    )

    if value is None:
        raise LookupError(
            f"'{name}' est introuvable dans la table {table}."
        )

    return int(value)


def write_log(
    user_id: int,
    action_type: str,
    description: str,
    cursor=None,
) -> None:
    """Ajoute une action dans le journal de traçabilité."""
    query = """
        INSERT INTO logs (
            user_id,
            action_type,
            action_description
        )
        VALUES (%s, %s, %s)
    """

    values = (user_id, action_type, description)

    if cursor is not None:
        cursor.execute(query, values)
    else:
        with mysql_transaction() as (_, local_cursor):
            local_cursor.execute(query, values)


# -----------------------------------------------------------------------------
# IDENTITÉ LOCALE DE L'APPLICATION — SANS AUTHENTIFICATION
# -----------------------------------------------------------------------------
def get_application_user() -> Dict[str, Any]:
    """
    Retourne l'utilisateur local utilisé pour la traçabilité.

    L'application ne demande plus d'adresse e-mail ni de mot de passe.
    Le premier utilisateur actif enregistré dans MySQL est utilisé pour :
    - préremplir le nom de l'inspecteur ;
    - associer les actions à la table logs.

    Si aucun utilisateur n'existe, l'application utilise une identité système.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT user_id, full_name, email, role, is_active
            FROM users
            WHERE is_active = TRUE
            ORDER BY
                CASE WHEN role = 'Administrateur' THEN 0 ELSE 1 END,
                user_id
            LIMIT 1
            """
        )
        user = cursor.fetchone()

        if user:
            return user

        return {
            "user_id": None,
            "full_name": "Utilisateur local",
            "email": "",
            "role": "Local",
            "is_active": True,
        }

    finally:
        cursor.close()
        conn.close()


def get_application_user_id() -> Optional[int]:
    """Renvoie l'identifiant utilisé dans les journaux d'activité."""
    return get_application_user().get("user_id")


def get_application_user_name() -> str:
    """Renvoie le nom affiché par défaut dans les formulaires."""
    return str(get_application_user().get("full_name") or "Utilisateur local")


# -----------------------------------------------------------------------------
# CHARGEMENT DES MODÈLES
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_mobilenet_model():
    if not MOBILENET_MODEL_PATH.exists():
        raise FileNotFoundError(f"Modèle introuvable : {MOBILENET_MODEL_PATH}")
    return load_model(MOBILENET_MODEL_PATH, compile=False)


@st.cache_resource(show_spinner=False)
def load_efficientnet_model():
    if not EFFICIENTNET_MODEL_PATH.exists():
        raise FileNotFoundError(f"Modèle introuvable : {EFFICIENTNET_MODEL_PATH}")
    return load_model(EFFICIENTNET_MODEL_PATH, compile=False)


def predict_mobilenet(image: Image.Image) -> Dict[str, Any]:
    """Niveau 1 : classification binaire Crack / No Crack."""
    model = load_mobilenet_model()
    resized = image.resize((300, 300))
    batch = np.expand_dims(np.asarray(resized, dtype=np.float32), axis=0)

    start = time.perf_counter()
    output = np.asarray(model.predict(batch, verbose=0)).reshape(-1)
    inference_time = time.perf_counter() - start

    # Compatible avec une sortie sigmoïde (1 valeur) ou softmax (2 valeurs).
    if output.size == 1:
        probability_crack = float(output[0])
    elif output.size == 2:
        probability_crack = float(output[1])
    else:
        raise ValueError(
            f"Sortie MobileNetV2 inattendue : {output.shape}. "
            "Le modèle doit retourner 1 ou 2 probabilités."
        )

    is_crack = probability_crack >= MOBILENET_CRACK_THRESHOLD
    return {
        "model_name": "MobileNetV2",
        "class_name": "Crack" if is_crack else "No Crack",
        "confidence": probability_crack if is_crack else 1.0 - probability_crack,
        "raw_probability": probability_crack,
        "inference_time": inference_time,
        "priority": "Moyenne" if is_crack else "Faible",
        "recommendation": (
            "Une fissure a été détectée. Une classification détaillée des défauts "
            "est lancée automatiquement."
            if is_crack
            else "Aucune fissure significative détectée. Aucune intervention immédiate."
        ),
        "trigger_level_2": is_crack,
    }


def predict_efficientnet(image: Image.Image) -> List[Dict[str, Any]]:
    """
    Niveau 2 : identification de la nature du défaut avec EfficientNetB3.

    Les six sorties CODEBRIM sont conservées, y compris Background. Le niveau 2
    peut ainsi corriger un faux positif du détecteur binaire de niveau 1.
    """
    model = load_efficientnet_model()

    resized = image.resize((300, 300))
    image_array = np.asarray(resized, dtype=np.float32)
    batch = np.expand_dims(
        preprocess_input(image_array),
        axis=0,
    )

    start = time.perf_counter()
    probabilities = np.asarray(
        model.predict(batch, verbose=0)
    ).reshape(-1)
    inference_time = time.perf_counter() - start

    if len(probabilities) != len(CODEBRIM_LABELS):
        raise ValueError(
            f"Le modèle EfficientNetB3 retourne {len(probabilities)} sorties, "
            f"mais {len(CODEBRIM_LABELS)} labels sont configurés."
        )

    detected: List[Dict[str, Any]] = []

    for label in CODEBRIM_LABELS:
        label_index = CODEBRIM_LABELS.index(label)
        probability = float(probabilities[label_index])
        threshold = CODEBRIM_THRESHOLDS[label]

        if probability >= threshold:
            mapping = CODEBRIM_CLASS_MAPPING[label]

            detected.append(
                {
                    "model_name": "EfficientNetB3",
                    "original_label": label,
                    "class_name": mapping["db_name"],
                    "confidence": probability,
                    "threshold": threshold,
                    "inference_time": inference_time,
                    "priority": mapping["priority"],
                    "recommendation": mapping["recommendation"],
                }
            )

    # Background est exclusif : si un défaut franchit aussi son seuil, le
    # résultat métier conserve le ou les défauts plutôt que Background.
    if len(detected) > 1:
        non_background = [
            result for result in detected
            if result["original_label"] != "Background"
        ]
        if non_background:
            detected = non_background

    # Si aucune classe ne dépasse son seuil optimisé, retenir la sortie la plus
    # probable parmi les six classes sans masquer artificiellement Background.
    if not detected:
        best_index = max(
            range(len(CODEBRIM_LABELS)),
            key=lambda index: float(probabilities[index]),
        )

        best_label = CODEBRIM_LABELS[best_index]
        best_probability = float(probabilities[best_index])
        mapping = CODEBRIM_CLASS_MAPPING[best_label]

        detected.append(
            {
                "model_name": "EfficientNetB3",
                "original_label": best_label,
                "class_name": mapping["db_name"],
                "confidence": best_probability,
                "threshold": CODEBRIM_THRESHOLDS[best_label],
                "inference_time": inference_time,
                "priority": mapping["priority"],
                "recommendation": (
                    mapping["recommendation"]
                    + " Aucun seuil optimisé n'ayant été dépassé, "
                    + "la classe de défaut la plus probable a été retenue."
                ),
            }
        )

    # Trier les défauts du plus probable au moins probable.
    detected.sort(
        key=lambda result: result["confidence"],
        reverse=True,
    )

    return detected


def run_two_level_pipeline(image: Image.Image) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Exécute automatiquement le niveau 1 puis, si nécessaire, le niveau 2."""
    level_1 = predict_mobilenet(image)
    level_2: List[Dict[str, Any]] = []
    if level_1["trigger_level_2"]:
        level_2 = predict_efficientnet(image)
    return level_1, level_2


# -----------------------------------------------------------------------------
# ENREGISTREMENT D'UNE ANALYSE
# -----------------------------------------------------------------------------
def save_analysis(
    inspection_id: int,
    image: Image.Image,
    original_filename: str,
    level_1: Dict[str, Any],
    level_2: List[Dict[str, Any]],
    user_id: int,
) -> Dict[str, Any]:
    """Sauvegarde image, prédictions, rapports et log dans une seule transaction."""
    extension = Path(original_filename).suffix.lower() or ".jpg"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"inspection_{inspection_id}_{timestamp}{extension}"
    image_path = UPLOAD_DIR / filename
    image.save(image_path)

    model_1_id = get_id_by_name("models", "model_id", "model_name", "MobileNetV2")
    dataset_1_id = get_id_by_name(
        "datasets", "dataset_id", "dataset_name", "Surface Crack Detection"
    )

    final_results = level_2 if level_2 else [level_1]
    selected_dataset_id = (
        get_id_by_name("datasets", "dataset_id", "dataset_name", "CODEBRIM")
        if level_2
        else dataset_1_id
    )

    prediction_ids: List[int] = []
    report_ids: List[int] = []

    try:
        with mysql_transaction() as (_, cursor):
            cursor.execute(
                """
                INSERT INTO inspection_images
                    (inspection_id, dataset_id, image_name, image_path)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    inspection_id,
                    selected_dataset_id,
                    filename,
                    str(image_path.relative_to(BASE_DIR)).replace("\\", "/"),
                ),
            )
            image_id = int(cursor.lastrowid)

            # Le résultat du niveau 1 est toujours conservé pour la traçabilité.
            all_results: List[Dict[str, Any]] = [level_1] + level_2
            for result in all_results:
                model_id = (
                    model_1_id
                    if result["model_name"] == "MobileNetV2"
                    else get_id_by_name(
                        "models", "model_id", "model_name", "EfficientNetB3"
                    )
                )
                class_id = get_id_by_name(
                    "defect_classes", "class_id", "class_name", result["class_name"]
                )
                confidence_percent = round(float(result["confidence"]) * 100, 2)

                cursor.execute(
                    """
                    INSERT INTO predictions
                        (image_id, model_id, predicted_class, confidence)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (image_id, model_id, class_id, confidence_percent),
                )
                prediction_id = int(cursor.lastrowid)
                prediction_ids.append(prediction_id)

                cursor.execute(
                    """
                    INSERT INTO inspection_reports
                        (prediction_id, intervention_priority, recommendation)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        prediction_id,
                        result["priority"],
                        result["recommendation"],
                    ),
                )
                report_ids.append(int(cursor.lastrowid))

            write_log(
                user_id,
                "Prédiction IA",
                (
                    f"Analyse automatique à deux niveaux de l'image n°{image_id}. "
                    f"{len(prediction_ids)} prédiction(s) enregistrée(s)."
                ),
                cursor=cursor,
            )

        return {
            "image_id": image_id,
            "prediction_ids": prediction_ids,
            "report_ids": report_ids,
            "image_path": image_path,
            "final_results": final_results,
        }
    except Exception:
        # Évite de laisser un fichier orphelin si la transaction SQL échoue.
        if image_path.exists():
            image_path.unlink(missing_ok=True)
        raise



# -----------------------------------------------------------------------------
# EXPORTS PROFESSIONNELS
# -----------------------------------------------------------------------------
def dataframe_to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    """Convertit un DataFrame en CSV UTF-8 compatible avec Excel."""
    return dataframe.to_csv(
        index=False,
        sep=";",
        encoding="utf-8-sig",
    ).encode("utf-8-sig")


def dataframe_to_excel_bytes(
    dataframe: pd.DataFrame,
    sheet_name: str = "Données",
) -> bytes:
    """
    Convertit un DataFrame en fichier Excel en mémoire.

    Nécessite le paquet openpyxl :
        python -m pip install openpyxl
    """
    output = io.BytesIO()

    try:
        with pd.ExcelWriter(
            output,
            engine="openpyxl",
        ) as writer:
            dataframe.to_excel(
                writer,
                index=False,
                sheet_name=sheet_name[:31],
            )

            worksheet = writer.book[sheet_name[:31]]

            # Ajustement automatique simple de la largeur des colonnes.
            for column_cells in worksheet.columns:
                maximum_length = 0
                column_letter = column_cells[0].column_letter

                for cell in column_cells:
                    cell_value = "" if cell.value is None else str(cell.value)
                    maximum_length = max(
                        maximum_length,
                        min(len(cell_value), 60),
                    )

                worksheet.column_dimensions[column_letter].width = (
                    maximum_length + 2
                )

    except ImportError as exc:
        raise RuntimeError(
            "Le paquet openpyxl est absent. "
            "Installe-le avec : python -m pip install openpyxl"
        ) from exc

    output.seek(0)
    return output.getvalue()


def image_to_download_bytes(image_path: Path) -> Tuple[bytes, str]:
    """Lit une image et renvoie ses octets ainsi que son type MIME."""
    if not image_path.exists():
        raise FileNotFoundError(
            f"Image introuvable : {image_path}"
        )

    extension = image_path.suffix.lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    return image_path.read_bytes(), mime_types.get(
        extension,
        "application/octet-stream",
    )


def build_complete_export_zip() -> bytes:
    """
    Construit une archive ZIP contenant les principaux exports métier :
    - inspections CSV ;
    - historique des prédictions CSV ;
    - rapports CSV ;
    - modèles CSV ;
    - logs CSV.
    """
    export_queries = {
        "inspections.csv": """
            SELECT
                i.inspection_id,
                i.inspection_date,
                i.location,
                i.infrastructure_type,
                i.inspector_name,
                i.weather_conditions,
                i.status,
                d.drone_name,
                d.drone_model,
                i.description,
                i.created_at
            FROM inspections i
            LEFT JOIN drones d
                ON i.drone_id = d.drone_id
            ORDER BY i.inspection_date DESC, i.inspection_id DESC
        """,
        "historique_predictions.csv": HISTORY_QUERY,
        "rapports_inspection.csv": REPORTS_QUERY,
        "modeles_ia.csv": """
            SELECT *
            FROM models
            ORDER BY model_id
        """,
        "journal_activite.csv": """
            SELECT
                l.log_id,
                COALESCE(u.full_name, 'Application locale') AS utilisateur,
                l.action_type,
                l.action_description,
                l.action_date
            FROM logs l
            LEFT JOIN users u
                ON l.user_id = u.user_id
            ORDER BY l.action_date DESC, l.log_id DESC
        """,
    }

    buffer = io.BytesIO()

    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for filename, query in export_queries.items():
            dataframe = read_dataframe(query)
            archive.writestr(
                filename,
                dataframe_to_csv_bytes(dataframe),
            )

        readme = (
            "DroneInspect AI — Export complet\n"
            "================================\n\n"
            "Cette archive contient les données métier exportées depuis MySQL.\n"
            f"Date de génération : {datetime.now():%d/%m/%Y %H:%M:%S}\n"
        )

        archive.writestr(
            "LISEZ_MOI.txt",
            readme.encode("utf-8"),
        )

    buffer.seek(0)
    return buffer.getvalue()


def render_export_buttons(
    dataframe: pd.DataFrame,
    base_filename: str,
    excel_sheet_name: str = "Données",
) -> None:
    """Affiche les boutons d'export CSV et Excel d'un DataFrame."""
    export_col1, export_col2 = st.columns(2)

    with export_col1:
        st.download_button(
            "📥 Télécharger en CSV",
            data=dataframe_to_csv_bytes(dataframe),
            file_name=f"{base_filename}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with export_col2:
        try:
            excel_bytes = dataframe_to_excel_bytes(
                dataframe,
                sheet_name=excel_sheet_name,
            )

            st.download_button(
                "📊 Télécharger en Excel",
                data=excel_bytes,
                file_name=f"{base_filename}.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
            )

        except RuntimeError as exc:
            st.warning(str(exc))



# -----------------------------------------------------------------------------
# RAPPORT PDF
# -----------------------------------------------------------------------------
def generate_report_pdf(report_row: Dict[str, Any]) -> bytes:
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError(
            "ReportLab n'est pas installé. Exécute : pip install reportlab"
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCenter", parent=styles["Title"], alignment=TA_CENTER, spaceAfter=16
    )

    story: List[Any] = [
        Paragraph("DroneInspect AI", title_style),
        Paragraph("Rapport d'inspection assistée par intelligence artificielle", styles["Heading2"]),
        Spacer(1, 10),
    ]

    image_path = BASE_DIR / str(report_row.get("image_path", ""))
    if image_path.exists():
        try:
            img = RLImage(str(image_path), width=12 * cm, height=8 * cm)
            story.extend([img, Spacer(1, 12)])
        except Exception:
            pass

    data = [
        ["Champ", "Valeur"],
        ["Rapport", str(report_row.get("report_id", ""))],
        ["Inspection", str(report_row.get("inspection_id", ""))],
        ["Date", str(report_row.get("inspection_date", ""))],
        ["Lieu", str(report_row.get("location", ""))],
        ["Infrastructure", str(report_row.get("infrastructure_type", ""))],
        ["Inspecteur", str(report_row.get("inspector_name", ""))],
        ["Drone", str(report_row.get("drone", ""))],
        ["Modèle IA", str(report_row.get("model_name", ""))],
        ["Classe détectée", str(report_row.get("class_name", ""))],
        ["Confiance", f"{float(report_row.get('confidence', 0)):.2f} %"],
        ["Priorité", str(report_row.get("intervention_priority", ""))],
        ["Recommandation", str(report_row.get("recommendation", ""))],
    ]

    table = Table(data, colWidths=[5 * cm, 12 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#eaf2f8")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([table, Spacer(1, 18)])
    story.append(
        Paragraph(
            "Important : ce résultat constitue une aide à la décision. "
            "Toute intervention doit être validée par un professionnel compétent.",
            styles["BodyText"],
        )
    )
    doc.build(story)
    return buffer.getvalue()


# -----------------------------------------------------------------------------
# REQUÊTES MÉTIER
# -----------------------------------------------------------------------------
HISTORY_QUERY = """
    SELECT
        p.prediction_id,
        p.prediction_date,
        i.inspection_id,
        i.inspection_date,
        i.location,
        i.infrastructure_type,
        ii.image_name,
        ii.image_path,
        m.model_name,
        dc.class_name,
        p.confidence,
        ir.intervention_priority,
        ir.recommendation
    FROM predictions p
    INNER JOIN inspection_images ii ON p.image_id = ii.image_id
    LEFT JOIN inspections i ON ii.inspection_id = i.inspection_id
    INNER JOIN models m ON p.model_id = m.model_id
    INNER JOIN defect_classes dc ON p.predicted_class = dc.class_id
    LEFT JOIN inspection_reports ir ON p.prediction_id = ir.prediction_id
    ORDER BY p.prediction_date DESC, p.prediction_id DESC
"""

REPORTS_QUERY = """
    SELECT
        ir.report_id,
        ir.created_at,
        p.prediction_id,
        p.prediction_date,
        p.confidence,
        m.model_name,
        dc.class_name,
        ir.intervention_priority,
        ir.recommendation,
        ii.image_name,
        ii.image_path,
        i.inspection_id,
        i.inspection_date,
        i.location,
        i.infrastructure_type,
        i.inspector_name,
        CONCAT(d.drone_name, ' - ', d.drone_model) AS drone
    FROM inspection_reports ir
    INNER JOIN predictions p ON ir.prediction_id = p.prediction_id
    INNER JOIN models m ON p.model_id = m.model_id
    INNER JOIN defect_classes dc ON p.predicted_class = dc.class_id
    INNER JOIN inspection_images ii ON p.image_id = ii.image_id
    LEFT JOIN inspections i ON ii.inspection_id = i.inspection_id
    LEFT JOIN drones d ON i.drone_id = d.drone_id
    ORDER BY ir.created_at DESC, ir.report_id DESC
"""


# -----------------------------------------------------------------------------
# PAGES STREAMLIT
# -----------------------------------------------------------------------------

def page_home() -> None:
    render_hero(
        "🚁 DroneInspect AI",
        (
            "Plateforme intelligente d'inspection des infrastructures : "
            "gestion des missions, analyse automatique des images, "
            "priorisation des interventions et génération de rapports."
        ),
        [
            "Base MySQL connectée",
            "MobileNetV2 opérationnel",
            "EfficientNetB3 opérationnel",
            "Pipeline IA automatique",
        ],
    )

    tables = {
        "Datasets": "datasets",
        "Images analysées": "inspection_images",
        "Inspections": "inspections",
        "Modèles IA": "models",
        "Prédictions": "predictions",
        "Rapports": "inspection_reports",
    }

    values = {
        label: int(fetch_one_value(f"SELECT COUNT(*) FROM {table}") or 0)
        for label, table in tables.items()
    }

    avg_confidence = float(
        fetch_one_value(
            "SELECT COALESCE(AVG(confidence), 0) FROM predictions"
        )
        or 0
    )

    critical_count = int(
        fetch_one_value(
            """
            SELECT COUNT(*)
            FROM inspection_reports
            WHERE intervention_priority = 'Critique'
            """
        )
        or 0
    )

    render_kpis(
        [
            ("📋 Inspections", values["Inspections"], "Missions enregistrées"),
            ("🖼️ Images", values["Images analysées"], "Images analysées"),
            ("🤖 Prédictions", values["Prédictions"], "Résultats IA"),
            ("📄 Rapports", values["Rapports"], "Rapports disponibles"),
            ("🎯 Confiance moyenne", f"{avg_confidence:.2f} %", "Toutes prédictions"),
            ("🔴 Défauts critiques", critical_count, "Interventions urgentes"),
            ("🧠 Modèles IA", values["Modèles IA"], "Modèles référencés"),
            ("📂 Datasets", values["Datasets"], "Sources de données"),
        ]
    )

    st.markdown(
        '<div class="section-title">Pipeline d’analyse automatique</div>',
        unsafe_allow_html=True,
    )

    pipeline_col1, pipeline_col2, pipeline_col3 = st.columns(3)

    with pipeline_col1:
        with st.container(border=True):
            st.markdown("### 1. Image capturée")
            st.caption("Image issue d'une mission d'inspection")

    with pipeline_col2:
        with st.container(border=True):
            st.markdown("### 2. MobileNetV2")
            st.caption("Détection binaire : Crack / No Crack")

    with pipeline_col3:
        with st.container(border=True):
            st.markdown("### 3. EfficientNetB3")
            st.caption("Nature du défaut uniquement si Crack est détecté")

    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.markdown(
            '<div class="section-title">Dernières prédictions</div>',
            unsafe_allow_html=True,
        )
        latest = read_dataframe(HISTORY_QUERY + " LIMIT 5")

        if latest.empty:
            st.info("Aucune prédiction disponible.")
        else:
            latest_display = latest[
                [
                    "prediction_date",
                    "location",
                    "model_name",
                    "class_name",
                    "confidence",
                    "intervention_priority",
                ]
            ].rename(
                columns={
                    "prediction_date": "Date",
                    "location": "Lieu",
                    "model_name": "Modèle",
                    "class_name": "Classe",
                    "confidence": "Confiance (%)",
                    "intervention_priority": "Priorité",
                }
            )

            st.dataframe(
                latest_display,
                use_container_width=True,
                hide_index=True,
            )

    with col_right:
        st.markdown(
            '<div class="section-title">État du système</div>',
            unsafe_allow_html=True,
        )

        model_status = [
            ("MobileNetV2", MOBILENET_MODEL_PATH.exists()),
            ("EfficientNetB3", EFFICIENTNET_MODEL_PATH.exists()),
            ("Dossier uploads", UPLOAD_DIR.exists()),
            ("Rapports PDF", REPORTLAB_AVAILABLE),
        ]

        for label, available in model_status:
            icon = "✅" if available else "⚠️"
            status = "Opérationnel" if available else "À vérifier"

            with st.container(border=True):
                st.markdown(f"**{icon} {label}**")
                st.caption(status)

def page_datasets() -> None:
    st.title("📂 Jeux de données")
    st.dataframe(read_dataframe("SELECT * FROM datasets ORDER BY dataset_id"), use_container_width=True, hide_index=True)


def page_drones() -> None:
    st.title("🚁 Drones")
    st.dataframe(read_dataframe("SELECT * FROM drones ORDER BY drone_id"), use_container_width=True, hide_index=True)


def page_inspections() -> None:
    st.title("📋 Gestion des inspections")
    tab_create, tab_history = st.tabs(["➕ Nouvelle inspection", "📚 Historique"])

    with tab_create:

        drones = read_dataframe(
            "SELECT drone_id, drone_name, drone_model FROM drones ORDER BY drone_name"
        )
        if drones.empty:
            st.warning("Ajoutez d'abord un drone dans MySQL.")
            return

        drone_options = {
            f"{row.drone_name} — {row.drone_model}": int(row.drone_id)
            for row in drones.itertuples()
        }

        with st.form("inspection_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                inspection_date = st.date_input("Date de l'inspection")
                location = st.text_input("Lieu", placeholder="Pont urbain, Île-de-France")
                infrastructure_type = st.selectbox(
                    "Type d'infrastructure", ["Pont", "Toiture", "Pylône", "Bâtiment", "Autre"]
                )
                drone_label = st.selectbox("Drone utilisé", list(drone_options.keys()))
            with c2:
                inspector_name = st.text_input(
                    "Inspecteur", value=get_application_user_name()
                )
                weather = st.text_input("Conditions météorologiques")
                status = st.selectbox(
                    "Statut", ["Planifiée", "En cours", "Terminée", "Annulée"]
                )
                description = st.text_area("Description")
            submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

        if submitted:
            if not location.strip() or not inspector_name.strip():
                st.error("Le lieu et le nom de l'inspecteur sont obligatoires.")
            else:
                try:
                    with mysql_transaction() as (_, cursor):
                        cursor.execute(
                            """
                            INSERT INTO inspections
                                (drone_id, inspection_date, location, infrastructure_type,
                                 inspector_name, weather_conditions, status, description)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                drone_options[drone_label],
                                inspection_date,
                                location.strip(),
                                infrastructure_type,
                                inspector_name.strip(),
                                weather.strip(),
                                status,
                                description.strip(),
                            ),
                        )
                        inspection_id = int(cursor.lastrowid)
                        write_log(
                            get_application_user_id(),
                            "Création inspection",
                            f"Création de l'inspection n°{inspection_id} à {location.strip()}.",
                            cursor=cursor,
                        )
                    st.success(f"Inspection n°{inspection_id} enregistrée.")
                except Exception as exc:
                    st.error("Échec de l'enregistrement de l'inspection.")
                    st.exception(exc)

    with tab_history:
        df = read_dataframe(
            """
            SELECT i.inspection_id AS ID, i.inspection_date AS Date,
                   i.location AS Lieu, i.infrastructure_type AS Infrastructure,
                   i.inspector_name AS Inspecteur, i.weather_conditions AS Météo,
                   i.status AS Statut, d.drone_name AS Drone,
                   d.drone_model AS `Modèle du drone`, i.description AS Description
            FROM inspections i
            LEFT JOIN drones d ON i.drone_id = d.drone_id
            ORDER BY i.inspection_date DESC, i.inspection_id DESC
            """
        )
        st.dataframe(df, use_container_width=True, hide_index=True)



def page_classification() -> None:
    render_hero(
        "📸 Station d'analyse IA",
        (
            "Importez une image d'inspection. MobileNetV2 détecte une fissure, "
            "puis EfficientNetB3 identifie précisément la nature des défauts."
        ),
        [
            "Analyse automatique",
            "Enregistrement MySQL",
            "Pipeline à deux niveaux",
        ],
    )

    inspections = read_dataframe(
        """
        SELECT
            i.inspection_id,
            i.inspection_date,
            i.location,
            i.infrastructure_type,
            i.inspector_name,
            d.drone_name,
            d.drone_model
        FROM inspections i
        LEFT JOIN drones d ON i.drone_id = d.drone_id
        WHERE i.status <> 'Annulée'
        ORDER BY i.inspection_id DESC
        """
    )

    if inspections.empty:
        st.warning("Créez d'abord une inspection.")
        return

    options = {
        (
            f"Inspection n°{r.inspection_id} — "
            f"{r.inspection_date} — {r.location}"
        ): int(r.inspection_id)
        for r in inspections.itertuples()
    }

    with st.container(border=True):
        st.markdown(
            """
            <div class="analysis-form-heading">
                <div>
                    <h2>Nouvelle analyse</h2>
                    <p>Sélectionnez une mission et déposez une image de l’infrastructure.</p>
                </div>
                <span class="analysis-step-badge">ÉTAPE 1</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected = st.selectbox(
            "Mission d'inspection",
            list(options.keys()),
        )
        inspection_id = options[selected]

        uploaded_file = st.file_uploader(
            "Image de l'infrastructure",
            type=["jpg", "jpeg", "png", "webp"],
            help="Formats acceptés : JPG, PNG et WEBP.",
        )

        launch_analysis = st.button(
            "🤖 Lancer l'analyse automatique",
            type="primary",
            use_container_width=True,
        )

    if uploaded_file is None:
        st.info("Importez une image pour lancer l'analyse.")
        return

    image = Image.open(uploaded_file).convert("RGB")

    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown(
            '<div class="section-title">Aperçu de l’image</div>',
            unsafe_allow_html=True,
        )
        st.image(
            image,
            caption=uploaded_file.name,
            use_container_width=True,
        )

    with right:
        st.markdown(
            '<div class="section-title">État du pipeline</div>',
            unsafe_allow_html=True,
        )

        status_html = f"""
        <div class="content-card">
            <p><b>✅ MobileNetV2</b><br>
            <span class="small-note">Modèle disponible : {MOBILENET_MODEL_PATH.name}</span></p>
            <p><b>✅ EfficientNetB3</b><br>
            <span class="small-note">Lancé uniquement si une fissure est détectée</span></p>
            <p><b>✅ Base MySQL</b><br>
            <span class="small-note">Image, prédictions et rapports seront enregistrés</span></p>
            <p><b>ℹ️ Classes CODEBRIM</b><br>
            <span class="small-note">Crack, Spallation, Efflorescence, Exposed Rebar et Corrosion</span></p>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)

    if launch_analysis:
        try:
            progress = st.progress(10, text="Préparation de l'image...")

            with st.spinner("Niveau 1 : analyse avec MobileNetV2..."):
                level_1, level_2 = run_two_level_pipeline(image)

            progress.progress(70, text="Enregistrement des résultats...")

            saved = save_analysis(
                inspection_id=inspection_id,
                image=image,
                original_filename=uploaded_file.name,
                level_1=level_1,
                level_2=level_2,
                user_id=get_application_user_id(),
            )

            progress.progress(100, text="Analyse terminée")

            st.success(
                f"Analyse terminée — image n°{saved['image_id']} enregistrée."
            )

            st.markdown(
                '<div class="section-title">Résultat du niveau 1</div>',
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                result_col1, result_col2, result_col3 = st.columns(3)

                result_col1.metric(
                    "Classe détectée",
                    level_1["class_name"],
                )
                result_col2.metric(
                    "Confiance",
                    f"{level_1['confidence'] * 100:.2f} %",
                )
                result_col3.metric(
                    "Temps d'inférence",
                    f"{level_1['inference_time']:.3f} s",
                )

                st.write(f"**Priorité :** {level_1['priority']}")
                st.write(
                    f"**Recommandation :** {level_1['recommendation']}"
                )

            saved_image_path = Path(saved["image_path"])

            if saved_image_path.exists():
                image_bytes, image_mime = image_to_download_bytes(
                    saved_image_path
                )

                st.download_button(
                    "🖼️ Télécharger l'image analysée",
                    data=image_bytes,
                    file_name=saved_image_path.name,
                    mime=image_mime,
                    use_container_width=True,
                )

            if level_2:
                st.markdown(
                    '<div class="section-title">Niveau 2 — Nature du défaut détecté</div>',
                    unsafe_allow_html=True,
                )

                for index, result in enumerate(level_2, start=1):
                    with st.container(border=True):
                        st.markdown(
                            f"### Classe {index} — {result['original_label']}"
                        )

                        defect_col1, defect_col2 = st.columns(2)

                        defect_col1.metric(
                            "Confiance",
                            f"{result['confidence'] * 100:.2f} %",
                        )
                        defect_col2.metric(
                            "Priorité",
                            result["priority"],
                        )

                        st.write(
                            f"**Recommandation :** {result['recommendation']}"
                        )
            else:
                st.info(
                    "Aucune fissure détectée : EfficientNetB3 n'a pas été lancé."
                )

        except Exception as exc:
            st.error("Une erreur est survenue pendant l'analyse.")
            st.exception(exc)


def page_history() -> None:
    render_hero(
        "📊 Historique des analyses",
        (
            "Consultez l'ensemble des prédictions, filtrez les résultats "
            "et retrouvez rapidement les anomalies importantes."
        ),
        ["Filtres métier", "Traçabilité complète", "Données MySQL"],
    )

    df = read_dataframe(HISTORY_QUERY)

    if df.empty:
        st.info("Aucune prédiction enregistrée.")
        return

    c1, c2, c3, c4 = st.columns(4)

    class_filter = c1.multiselect(
        "Classe",
        sorted(df["class_name"].dropna().unique()),
    )
    model_filter = c2.multiselect(
        "Modèle",
        sorted(df["model_name"].dropna().unique()),
    )
    priority_filter = c3.multiselect(
        "Priorité",
        sorted(df["intervention_priority"].dropna().unique()),
    )
    location_filter = c4.multiselect(
        "Lieu",
        sorted(df["location"].dropna().unique()),
    )

    filtered = df.copy()

    if class_filter:
        filtered = filtered[filtered["class_name"].isin(class_filter)]
    if model_filter:
        filtered = filtered[filtered["model_name"].isin(model_filter)]
    if priority_filter:
        filtered = filtered[
            filtered["intervention_priority"].isin(priority_filter)
        ]
    if location_filter:
        filtered = filtered[filtered["location"].isin(location_filter)]

    render_kpis(
        [
            ("Résultats affichés", len(filtered), "Après application des filtres"),
            (
                "Confiance moyenne",
                f"{filtered['confidence'].mean():.2f} %" if not filtered.empty else "0 %",
                "Sur la sélection",
            ),
            (
                "Critiques",
                int(
                    (
                        filtered["intervention_priority"] == "Critique"
                    ).sum()
                ),
                "Anomalies prioritaires",
            ),
            (
                "Modèles utilisés",
                filtered["model_name"].nunique(),
                "Sur la sélection",
            ),
        ]
    )

    display = filtered.rename(
        columns={
            "prediction_date": "Date",
            "inspection_id": "Inspection",
            "location": "Lieu",
            "infrastructure_type": "Infrastructure",
            "image_name": "Image",
            "model_name": "Modèle",
            "class_name": "Classe",
            "confidence": "Confiance (%)",
            "intervention_priority": "Priorité",
            "recommendation": "Recommandation",
        }
    )

    st.dataframe(
        display[
            [
                "Date",
                "Inspection",
                "Lieu",
                "Infrastructure",
                "Image",
                "Modèle",
                "Classe",
                "Confiance (%)",
                "Priorité",
                "Recommandation",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


    export_dataframe = display[
        [
            "Date",
            "Inspection",
            "Lieu",
            "Infrastructure",
            "Image",
            "Modèle",
            "Classe",
            "Confiance (%)",
            "Priorité",
            "Recommandation",
        ]
    ]

    st.markdown("### Exporter l'historique filtré")

    render_export_buttons(
        export_dataframe,
        base_filename=(
            f"historique_predictions_"
            f"{datetime.now():%Y%m%d_%H%M%S}"
        ),
        excel_sheet_name="Historique",
    )


def page_reports() -> None:
    render_hero(
        "📄 Rapports d'intervention",
        (
            "Consultez les résultats métier, visualisez l'image analysée "
            "et téléchargez un rapport PDF prêt à être transmis."
        ),
        ["Rapports PDF", "Priorisation", "Recommandations métier"],
    )

    df = read_dataframe(REPORTS_QUERY)

    if df.empty:
        st.info("Aucun rapport disponible.")
        return

    report_options = {
        (
            f"Rapport n°{int(row.report_id)} — "
            f"{row.class_name} — {row.location}"
        ): int(row.report_id)
        for row in df.itertuples()
    }

    selected_label = st.selectbox(
        "Sélectionner un rapport",
        list(report_options.keys()),
    )

    report_id = report_options[selected_label]
    row = df[df["report_id"] == report_id].iloc[0].to_dict()

    left, right = st.columns([0.95, 1.05])

    with left:
        image_path = BASE_DIR / str(row.get("image_path", ""))

        if image_path.exists():
            st.image(
                str(image_path),
                caption=row.get("image_name", "Image analysée"),
                use_container_width=True,
            )
        else:
            st.info("L'image associée n'est pas disponible sur le disque.")

    with right:
        with st.container(border=True):
            st.markdown(f"## Rapport n°{report_id}")

            report_col1, report_col2 = st.columns(2)

            with report_col1:
                st.write(f"**Inspection :** n°{row['inspection_id']}")
                st.write(f"**Lieu :** {row['location']}")
                st.write(
                    f"**Infrastructure :** {row['infrastructure_type']}"
                )
                st.write(f"**Modèle :** {row['model_name']}")

            with report_col2:
                st.write(f"**Défaut :** {row['class_name']}")
                st.write(
                    f"**Confiance :** {float(row['confidence']):.2f} %"
                )
                st.write(
                    f"**Priorité :** {row['intervention_priority']}"
                )

            st.write(f"**Recommandation :** {row['recommendation']}")

        download_col1, download_col2 = st.columns(2)

        with download_col1:
            if REPORTLAB_AVAILABLE:
                try:
                    pdf_bytes = generate_report_pdf(row)

                    st.download_button(
                        "📄 Télécharger le rapport PDF",
                        data=pdf_bytes,
                        file_name=(
                            f"rapport_inspection_{report_id}.pdf"
                        ),
                        mime="application/pdf",
                        use_container_width=True,
                    )

                except Exception as exc:
                    st.error(
                        "Le rapport PDF n'a pas pu être généré."
                    )
                    st.exception(exc)
            else:
                st.warning(
                    "ReportLab n'est pas installé. Exécutez : "
                    "python -m pip install reportlab"
                )

        with download_col2:
            image_path = BASE_DIR / str(
                row.get("image_path", "")
            )

            if image_path.exists():
                image_bytes, image_mime = image_to_download_bytes(
                    image_path
                )

                st.download_button(
                    "🖼️ Télécharger l'image",
                    data=image_bytes,
                    file_name=image_path.name,
                    mime=image_mime,
                    use_container_width=True,
                )
            else:
                st.button(
                    "🖼️ Image indisponible",
                    disabled=True,
                    use_container_width=True,
                )

    st.divider()
    st.markdown("### Exporter la liste complète des rapports")

    reports_export = df.copy()

    render_export_buttons(
        reports_export,
        base_filename=(
            f"rapports_inspection_"
            f"{datetime.now():%Y%m%d_%H%M%S}"
        ),
        excel_sheet_name="Rapports",
    )


def page_dashboard() -> None:
    render_hero(
        "📈 Tableau de bord opérationnel",
        (
            "Suivi global des inspections, des performances IA "
            "et des priorités d'intervention."
        ),
        ["Indicateurs temps réel", "Graphiques interactifs", "Aide à la décision"],
    )

    counts = {
        "Inspections": int(
            fetch_one_value("SELECT COUNT(*) FROM inspections") or 0
        ),
        "Images": int(
            fetch_one_value("SELECT COUNT(*) FROM inspection_images") or 0
        ),
        "Prédictions": int(
            fetch_one_value("SELECT COUNT(*) FROM predictions") or 0
        ),
        "Rapports": int(
            fetch_one_value("SELECT COUNT(*) FROM inspection_reports") or 0
        ),
        "Modèles": int(
            fetch_one_value("SELECT COUNT(*) FROM models") or 0
        ),
        "Drones": int(
            fetch_one_value("SELECT COUNT(*) FROM drones") or 0
        ),
    }

    avg_conf = float(
        fetch_one_value(
            "SELECT COALESCE(AVG(confidence), 0) FROM predictions"
        )
        or 0
    )

    critical = int(
        fetch_one_value(
            """
            SELECT COUNT(*)
            FROM inspection_reports
            WHERE intervention_priority = 'Critique'
            """
        )
        or 0
    )

    render_kpis(
        [
            ("📋 Inspections", counts["Inspections"], "Missions enregistrées"),
            ("🖼️ Images", counts["Images"], "Images stockées"),
            ("🤖 Prédictions", counts["Prédictions"], "Résultats IA"),
            ("📄 Rapports", counts["Rapports"], "Documents générés"),
            ("🎯 Confiance moyenne", f"{avg_conf:.2f} %", "Toutes prédictions"),
            ("🔴 Critiques", critical, "Interventions urgentes"),
            ("🧠 Modèles", counts["Modèles"], "Modèles actifs"),
            ("🚁 Drones", counts["Drones"], "Drones référencés"),
        ]
    )

    df_defects = read_dataframe(
        """
        SELECT dc.class_name AS classe, COUNT(*) AS nombre
        FROM predictions p
        JOIN defect_classes dc ON p.predicted_class = dc.class_id
        GROUP BY dc.class_name
        ORDER BY nombre DESC
        """
    )

    df_models = read_dataframe(
        """
        SELECT m.model_name AS modele, COUNT(*) AS nombre
        FROM predictions p
        JOIN models m ON p.model_id = m.model_id
        GROUP BY m.model_name
        ORDER BY nombre DESC
        """
    )

    df_priorities = read_dataframe(
        """
        SELECT intervention_priority AS priorite, COUNT(*) AS nombre
        FROM inspection_reports
        GROUP BY intervention_priority
        ORDER BY nombre DESC
        """
    )

    df_time = read_dataframe(
        """
        SELECT DATE(prediction_date) AS date_prediction, COUNT(*) AS nombre
        FROM predictions
        GROUP BY DATE(prediction_date)
        ORDER BY date_prediction
        """
    )

    df_confidence_models = read_dataframe(
        """
        SELECT
            m.model_name AS modele,
            AVG(p.confidence) AS confiance_moyenne
        FROM predictions p
        JOIN models m ON p.model_id = m.model_id
        GROUP BY m.model_name
        ORDER BY confiance_moyenne DESC
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        if not df_defects.empty:
            figure = px.bar(
                df_defects,
                x="classe",
                y="nombre",
                text="nombre",
                title="Répartition des défauts détectés",
                labels={
                    "classe": "Défaut",
                    "nombre": "Nombre",
                },
            )
            figure.update_traces(textposition="outside")
            figure.update_layout(
                showlegend=False,
                margin=dict(l=20, r=20, t=60, b=20),
            )
            st.plotly_chart(figure, use_container_width=True)

    with col2:
        if not df_models.empty:
            figure = px.pie(
                df_models,
                names="modele",
                values="nombre",
                hole=0.52,
                title="Utilisation des modèles IA",
            )
            figure.update_traces(textinfo="percent+label")
            figure.update_layout(
                margin=dict(l=20, r=20, t=60, b=20),
            )
            st.plotly_chart(figure, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        if not df_priorities.empty:
            figure = px.bar(
                df_priorities,
                x="priorite",
                y="nombre",
                text="nombre",
                title="Priorités d'intervention",
                labels={
                    "priorite": "Priorité",
                    "nombre": "Nombre",
                },
            )
            figure.update_traces(textposition="outside")
            figure.update_layout(
                showlegend=False,
                margin=dict(l=20, r=20, t=60, b=20),
            )
            st.plotly_chart(figure, use_container_width=True)

    with col4:
        if not df_confidence_models.empty:
            figure = px.bar(
                df_confidence_models,
                x="modele",
                y="confiance_moyenne",
                text_auto=".2f",
                title="Confiance moyenne par modèle",
                labels={
                    "modele": "Modèle",
                    "confiance_moyenne": "Confiance moyenne (%)",
                },
            )
            figure.update_layout(
                yaxis_range=[0, 100],
                showlegend=False,
                margin=dict(l=20, r=20, t=60, b=20),
            )
            st.plotly_chart(figure, use_container_width=True)

    if not df_time.empty:
        figure = px.line(
            df_time,
            x="date_prediction",
            y="nombre",
            markers=True,
            title="Évolution des prédictions dans le temps",
            labels={
                "date_prediction": "Date",
                "nombre": "Nombre de prédictions",
            },
        )
        figure.update_layout(
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(figure, use_container_width=True)

    st.markdown(
        '<div class="section-title">Dernières prédictions</div>',
        unsafe_allow_html=True,
    )

    latest = read_dataframe(HISTORY_QUERY + " LIMIT 10")

    if latest.empty:
        st.info("Aucune prédiction disponible.")
    else:
        latest_display = latest[
            [
                "prediction_date",
                "location",
                "infrastructure_type",
                "model_name",
                "class_name",
                "confidence",
                "intervention_priority",
            ]
        ].rename(
            columns={
                "prediction_date": "Date",
                "location": "Lieu",
                "infrastructure_type": "Infrastructure",
                "model_name": "Modèle",
                "class_name": "Classe",
                "confidence": "Confiance (%)",
                "intervention_priority": "Priorité",
            }
        )

        st.dataframe(
            latest_display,
            use_container_width=True,
            hide_index=True,
        )


        st.markdown("### Centre de téléchargement")

        download_col1, download_col2, download_col3 = st.columns(3)

        with download_col1:
            st.download_button(
                "📥 Dernières prédictions CSV",
                data=dataframe_to_csv_bytes(latest_display),
                file_name=(
                    f"dernieres_predictions_"
                    f"{datetime.now():%Y%m%d_%H%M%S}.csv"
                ),
                mime="text/csv",
                use_container_width=True,
            )

        with download_col2:
            try:
                latest_excel = dataframe_to_excel_bytes(
                    latest_display,
                    sheet_name="Prédictions",
                )

                st.download_button(
                    "📊 Dernières prédictions Excel",
                    data=latest_excel,
                    file_name=(
                        f"dernieres_predictions_"
                        f"{datetime.now():%Y%m%d_%H%M%S}.xlsx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                )

            except RuntimeError as exc:
                st.warning(str(exc))

        with download_col3:
            st.download_button(
                "🗂️ Export complet ZIP",
                data=build_complete_export_zip(),
                file_name=(
                    f"droneinspect_export_complet_"
                    f"{datetime.now():%Y%m%d_%H%M%S}.zip"
                ),
                mime="application/zip",
                use_container_width=True,
            )


def page_downloads() -> None:
    """Centre d'export centralisé de DroneInspect AI."""
    render_hero(
        "📥 Centre de téléchargements",
        (
            "Exportez les données de l'application dans des formats "
            "directement exploitables pour le mémoire, les audits "
            "et les équipes métier."
        ),
        [
            "CSV",
            "Excel",
            "ZIP complet",
            "Rapports PDF",
        ],
    )

    inspections = read_dataframe(
        """
        SELECT
            i.inspection_id AS `ID`,
            i.inspection_date AS `Date`,
            i.location AS `Lieu`,
            i.infrastructure_type AS `Infrastructure`,
            i.inspector_name AS `Inspecteur`,
            i.weather_conditions AS `Météo`,
            i.status AS `Statut`,
            d.drone_name AS `Drone`,
            d.drone_model AS `Modèle du drone`,
            i.description AS `Description`
        FROM inspections i
        LEFT JOIN drones d
            ON i.drone_id = d.drone_id
        ORDER BY i.inspection_date DESC, i.inspection_id DESC
        """
    )

    history = read_dataframe(HISTORY_QUERY)
    reports = read_dataframe(REPORTS_QUERY)
    logs = read_dataframe(
        """
        SELECT
            l.log_id AS `ID`,
            COALESCE(u.full_name, 'Application locale') AS `Utilisateur`,
            l.action_type AS `Action`,
            l.action_description AS `Description`,
            l.action_date AS `Date`
        FROM logs l
        LEFT JOIN users u
            ON l.user_id = u.user_id
        ORDER BY l.action_date DESC, l.log_id DESC
        """
    )

    tab_inspections, tab_history, tab_reports, tab_complete = st.tabs(
        [
            "📋 Inspections",
            "🤖 Prédictions",
            "📄 Rapports",
            "🗂️ Export complet",
        ]
    )

    with tab_inspections:
        st.dataframe(
            inspections,
            use_container_width=True,
            hide_index=True,
        )

        render_export_buttons(
            inspections,
            base_filename=(
                f"inspections_"
                f"{datetime.now():%Y%m%d_%H%M%S}"
            ),
            excel_sheet_name="Inspections",
        )

    with tab_history:
        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )

        render_export_buttons(
            history,
            base_filename=(
                f"predictions_"
                f"{datetime.now():%Y%m%d_%H%M%S}"
            ),
            excel_sheet_name="Prédictions",
        )

    with tab_reports:
        st.dataframe(
            reports,
            use_container_width=True,
            hide_index=True,
        )

        render_export_buttons(
            reports,
            base_filename=(
                f"rapports_"
                f"{datetime.now():%Y%m%d_%H%M%S}"
            ),
            excel_sheet_name="Rapports",
        )

    with tab_complete:
        render_kpis(
            [
                ("Inspections", len(inspections), "Missions exportables"),
                ("Prédictions", len(history), "Résultats IA"),
                ("Rapports", len(reports), "Rapports métier"),
                ("Logs", len(logs), "Actions tracées"),
            ]
        )

        st.info(
            "L'archive ZIP contient les inspections, les prédictions, "
            "les rapports, les modèles IA et les logs au format CSV."
        )

        st.download_button(
            "🗂️ Télécharger l'export complet ZIP",
            data=build_complete_export_zip(),
            file_name=(
                f"droneinspect_export_complet_"
                f"{datetime.now():%Y%m%d_%H%M%S}.zip"
            ),
            mime="application/zip",
            type="primary",
            use_container_width=True,
        )



def page_admin() -> None:
    """
    Administration locale.

    Cette page permet :
    - de consulter et ajouter des utilisateurs métier ;
    - de modifier leur rôle et leur statut ;
    - de consulter les modèles IA ;
    - de consulter les journaux d'activité.

    """
    st.title("⚙ Administration")

    tab_users, tab_models, tab_logs = st.tabs(
        [
            "👥 Utilisateurs",
            "🧠 Modèles",
            "📜 Logs",
        ]
    )

    # ------------------------------------------------------------------
    # UTILISATEURS
    # ------------------------------------------------------------------
    with tab_users:
        st.subheader("Gestion des utilisateurs métier")

        users = read_dataframe(
            """
            SELECT
                user_id AS `ID`,
                full_name AS `Nom complet`,
                email AS `E-mail`,
                role AS `Rôle`,
                is_active AS `Actif`,
                created_at AS `Créé le`
            FROM users
            ORDER BY user_id
            """
        )

        st.dataframe(
            users,
            use_container_width=True,
            hide_index=True,
        )

        col_add, col_edit = st.columns(2)

        with col_add:
            with st.container(border=True):
                st.markdown("### ➕ Ajouter un utilisateur")

                with st.form("add_local_user_form", clear_on_submit=True):
                    full_name = st.text_input("Nom complet")
                    email = st.text_input("Adresse e-mail")
                    role = st.selectbox(
                        "Rôle",
                        [
                            "Administrateur",
                            "Inspecteur",
                            "Observateur",
                        ],
                    )

                    submitted = st.form_submit_button(
                        "Créer l'utilisateur",
                        use_container_width=True,
                    )

                if submitted:
                    if not full_name.strip():
                        st.error("Le nom complet est obligatoire.")
                    elif "@" not in email or "." not in email:
                        st.error("L'adresse e-mail n'est pas valide.")
                    else:
                        try:
                            with mysql_transaction() as (_, cursor):
                                cursor.execute(
                                    """
                                    INSERT INTO users (
                                        full_name,
                                        email,
                                        password_hash,
                                        role,
                                        is_active
                                    )
                                    VALUES (%s, %s, NULL, %s, TRUE)
                                    """,
                                    (
                                        full_name.strip(),
                                        email.strip().lower(),
                                        role,
                                    ),
                                )

                                new_user_id = int(cursor.lastrowid)

                                write_log(
                                    get_application_user_id(),
                                    "Création utilisateur",
                                    (
                                        f"Création du compte métier n°{new_user_id} "
                                        f"({email.strip().lower()}) avec le rôle {role}."
                                    ),
                                    cursor=cursor,
                                )

                            st.success("Utilisateur créé avec succès.")
                            st.rerun()

                        except MySQLError as exc:
                            if getattr(exc, "errno", None) == 1062:
                                st.error(
                                    "Cette adresse e-mail est déjà utilisée."
                                )
                            else:
                                st.error(
                                    "Impossible de créer l'utilisateur."
                                )
                                st.exception(exc)

        with col_edit:
            with st.container(border=True):
                st.markdown("### ✏️ Modifier un utilisateur")

                user_rows = read_dataframe(
                    """
                    SELECT user_id, full_name, email, role, is_active
                    FROM users
                    ORDER BY full_name
                    """
                )

                if user_rows.empty:
                    st.info("Aucun utilisateur disponible.")
                else:
                    user_options = {
                        (
                            f"#{int(row.user_id)} — "
                            f"{row.full_name} — {row.email}"
                        ): int(row.user_id)
                        for row in user_rows.itertuples()
                    }

                    selected_label = st.selectbox(
                        "Utilisateur",
                        list(user_options.keys()),
                    )
                    selected_user_id = user_options[selected_label]

                    selected_row = user_rows[
                        user_rows["user_id"] == selected_user_id
                    ].iloc[0]

                    roles = [
                        "Administrateur",
                        "Inspecteur",
                        "Observateur",
                    ]

                    current_role = selected_row["role"]
                    role_index = roles.index(current_role) if current_role in roles else 1

                    new_role = st.selectbox(
                        "Nouveau rôle",
                        roles,
                        index=role_index,
                    )

                    new_status = st.checkbox(
                        "Compte actif",
                        value=bool(selected_row["is_active"]),
                    )

                    if st.button(
                        "Enregistrer les modifications",
                        use_container_width=True,
                    ):
                        try:
                            with mysql_transaction() as (_, cursor):
                                cursor.execute(
                                    """
                                    UPDATE users
                                    SET role = %s,
                                        is_active = %s
                                    WHERE user_id = %s
                                    """,
                                    (
                                        new_role,
                                        new_status,
                                        selected_user_id,
                                    ),
                                )

                                write_log(
                                    get_application_user_id(),
                                    "Modification utilisateur",
                                    (
                                        f"Modification du compte métier "
                                        f"n°{selected_user_id}. "
                                        f"Rôle={new_role}, actif={new_status}."
                                    ),
                                    cursor=cursor,
                                )

                            st.success("Utilisateur modifié avec succès.")
                            st.rerun()

                        except Exception as exc:
                            st.error(
                                "Impossible de modifier l'utilisateur."
                            )
                            st.exception(exc)

    # ------------------------------------------------------------------
    # MODÈLES
    # ------------------------------------------------------------------
    with tab_models:
        st.subheader("Modèles d'intelligence artificielle")

        models = read_dataframe(
            """
            SELECT
                model_id AS `ID`,
                model_name AS `Modèle`,
                model_type AS `Type`,
                task_type AS `Tâche`,
                input_size AS `Entrée`,
                classes_count AS `Classes`,
                model_path AS `Chemin`,
                accuracy AS `Accuracy`,
                created_at AS `Créé le`
            FROM models
            ORDER BY model_id
            """
        )

        st.dataframe(
            models,
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            "MobileNetV2 réalise la détection binaire au niveau 1. "
            "EfficientNetB3 est lancé automatiquement au niveau 2 "
            "lorsqu'une anomalie est détectée."
        )

    # ------------------------------------------------------------------
    # LOGS
    # ------------------------------------------------------------------
    with tab_logs:
        st.subheader("Journal d'activité")

        logs = read_dataframe(
            """
            SELECT
                l.log_id AS `ID`,
                COALESCE(u.full_name, 'Application locale') AS `Utilisateur`,
                l.action_type AS `Action`,
                l.action_description AS `Description`,
                l.action_date AS `Date`
            FROM logs l
            LEFT JOIN users u
                ON l.user_id = u.user_id
            ORDER BY l.action_date DESC, l.log_id DESC
            """
        )

        st.dataframe(
            logs,
            use_container_width=True,
            hide_index=True,
        )


# -----------------------------------------------------------------------------
# DÉMARRAGE DE L'APPLICATION
# -----------------------------------------------------------------------------
def main() -> None:
    """
    Point d'entrée de l'application.

    L'utilisateur doit être authentifié avant d'accéder au menu principal.
    """
    if not st.session_state.get("admin_authenticated", False):
        _, login_column, _ = st.columns([1, 1.2, 1])

        with login_column:
            st.markdown(
                """
                <div style="padding:1rem 0 1.5rem;text-align:center;">
                    <div style="font-size:2rem;font-weight:800;">
                        🚁 DroneInspect AI
                    </div>
                    <div style="font-size:0.95rem;opacity:0.78;margin-top:0.35rem;">
                        Plateforme d'inspection assistée par IA
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.subheader("Connexion administrateur")
            email = st.text_input("Adresse e-mail", key="admin_email")
            password = st.text_input(
                "Mot de passe",
                type="password",
                key="admin_password",
            )

            if st.button("Se connecter", type="primary"):
                if verify_admin_password(email, password):
                    st.session_state["admin_authenticated"] = True
                    st.rerun()
                else:
                    st.error("E-mail ou mot de passe administrateur incorrect.")
        st.stop()

    try:
        # Vérification simple de la connexion et de la structure principale.
        fetch_one_value("SELECT COUNT(*) FROM datasets")
    except Exception as exc:
        st.error("La base MySQL n'est pas accessible.")
        st.exception(exc)
        st.stop()

    local_user = get_application_user()

    st.sidebar.markdown(
        """
        <div style="padding:0.5rem 0 1rem;">
            <div style="font-size:1.45rem;font-weight:800;">🚁 DroneInspect AI</div>
            <div style="font-size:0.86rem;opacity:0.78;margin-top:0.25rem;">
                Plateforme d'inspection assistée par IA
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.caption(
        f"Traçabilité locale : {local_user['full_name']}"
    )
    if st.sidebar.button("Se déconnecter"):
        st.session_state["admin_authenticated"] = False
        st.rerun()

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Accueil",
            "📂 Datasets",
            "🚁 Drones",
            "📋 Inspections",
            "📸 Classification IA",
            "📊 Historique",
            "📄 Rapports",
            "📈 Dashboard",
            "📥 Téléchargements",
            "⚙ Administration",
            "📤 Import référentiel",
        ],
    )

    pages = {
        "🏠 Accueil": page_home,
        "📂 Datasets": page_datasets,
        "🚁 Drones": page_drones,
        "📋 Inspections": page_inspections,
        "📸 Classification IA": page_classification,
        "📊 Historique": page_history,
        "📄 Rapports": page_reports,
        "📈 Dashboard": page_dashboard,
        "📥 Téléchargements": page_downloads,
        "⚙ Administration": page_admin,
        "📤 Import référentiel": render_import_page,
    }

    try:
        pages[page]()
    except MySQLError as exc:
        st.error("Erreur MySQL.")
        st.exception(exc)
    except Exception as exc:
        st.error("Une erreur inattendue est survenue.")
        st.exception(exc)

if __name__ == "__main__":
    main()
