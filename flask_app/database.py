"""Accès MySQL et persistance des analyses/imports Flask."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import mysql.connector
from PIL import Image
from werkzeug.utils import secure_filename

from shared_config import BASE_DIR, get_mysql_config


UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def connect():
    return mysql.connector.connect(**get_mysql_config(), autocommit=False)


@contextmanager
def transaction(dictionary: bool = False):
    connection = connect()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def inspections() -> list[dict]:
    with transaction(dictionary=True) as cursor:
        cursor.execute(
            "SELECT inspection_id, inspection_date, location, infrastructure_type "
            "FROM inspections ORDER BY inspection_date DESC, inspection_id DESC"
        )
        return cursor.fetchall()


def drones() -> list[dict]:
    """Retourne les drones disponibles pour le formulaire d'inspection."""
    with transaction(dictionary=True) as cursor:
        cursor.execute(
            "SELECT drone_id, drone_name, drone_model FROM drones ORDER BY drone_name"
        )
        return cursor.fetchall()


def inspection_history() -> list[dict]:
    """Historique complet des inspections et du drone associé."""
    with transaction(dictionary=True) as cursor:
        cursor.execute(
            "SELECT i.inspection_id, i.inspection_date, i.location, "
            "i.infrastructure_type, i.inspector_name, i.weather_conditions, "
            "i.status, i.description, d.drone_name, d.drone_model "
            "FROM inspections i LEFT JOIN drones d ON i.drone_id=d.drone_id "
            "ORDER BY i.inspection_date DESC, i.inspection_id DESC"
        )
        return cursor.fetchall()


def create_inspection(data: dict) -> int:
    """Crée une inspection depuis le formulaire Flask et journalise l'action."""
    required = ("inspection_date", "location", "infrastructure_type", "inspector_name", "status")
    missing = [name for name in required if not str(data.get(name, "")).strip()]
    if missing:
        raise ValueError("Champs obligatoires manquants : " + ", ".join(missing))
    try:
        inspection_date = datetime.fromisoformat(str(data["inspection_date"])).date()
        drone_id = int(data["drone_id"])
    except (ValueError, TypeError) as exc:
        raise ValueError("Date ou drone invalide.") from exc
    with transaction() as cursor:
        cursor.execute("SELECT 1 FROM drones WHERE drone_id=%s", (drone_id,))
        if not cursor.fetchone():
            raise ValueError("Le drone sélectionné n'existe pas.")
        cursor.execute(
            "INSERT INTO inspections "
            "(drone_id,inspection_date,location,infrastructure_type,inspector_name,"
            "weather_conditions,status,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                drone_id, inspection_date, str(data["location"]).strip(),
                str(data["infrastructure_type"]).strip(), str(data["inspector_name"]).strip(),
                str(data.get("weather_conditions", "")).strip(), str(data["status"]).strip(),
                str(data.get("description", "")).strip() or None,
            ),
        )
        inspection_id = int(cursor.lastrowid)
        cursor.execute(
            "INSERT INTO logs (user_id,action_type,action_description) VALUES (%s,%s,%s)",
            (_application_user_id(cursor), "Création inspection Flask",
             f"Création de l'inspection n°{inspection_id} via Flask."),
        )
    return inspection_id


def fetch_rows(query: str, params: tuple = ()) -> list[dict]:
    """Exécute une requête SELECT interne et retourne des dictionnaires."""
    if not query.lstrip().upper().startswith("SELECT"):
        raise ValueError("Seules les requêtes SELECT internes sont autorisées.")
    with transaction(dictionary=True) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def datasets_list() -> list[dict]:
    return fetch_rows("SELECT * FROM datasets ORDER BY dataset_id")


def drones_list() -> list[dict]:
    return fetch_rows("SELECT * FROM drones ORDER BY drone_id")


def prediction_history(limit: int | None = 500) -> list[dict]:
    suffix = f" LIMIT {int(limit)}" if limit else ""
    return fetch_rows(
        "SELECT p.prediction_id, p.prediction_date, i.inspection_id, i.location, "
        "i.infrastructure_type, ii.image_name, m.model_name, dc.class_name, "
        "p.confidence, ir.intervention_priority, ir.recommendation "
        "FROM predictions p JOIN inspection_images ii ON p.image_id=ii.image_id "
        "LEFT JOIN inspections i ON ii.inspection_id=i.inspection_id "
        "JOIN models m ON p.model_id=m.model_id "
        "JOIN defect_classes dc ON p.predicted_class=dc.class_id "
        "LEFT JOIN inspection_reports ir ON p.prediction_id=ir.prediction_id "
        "ORDER BY p.prediction_date DESC, p.prediction_id DESC" + suffix
    )


def reports_list(limit: int | None = 500) -> list[dict]:
    suffix = f" LIMIT {int(limit)}" if limit else ""
    return fetch_rows(
        "SELECT ir.report_id, ir.created_at AS report_date, ir.intervention_priority, "
        "ir.recommendation, p.prediction_id, p.confidence, dc.class_name, "
        "m.model_name, ii.image_name, ii.image_path, i.inspection_id, "
        "i.inspection_date, i.location, i.infrastructure_type, i.inspector_name, "
        "CONCAT(d.drone_name, ' - ', d.drone_model) AS drone "
        "FROM inspection_reports ir JOIN predictions p ON ir.prediction_id=p.prediction_id "
        "JOIN defect_classes dc ON p.predicted_class=dc.class_id "
        "JOIN models m ON p.model_id=m.model_id "
        "JOIN inspection_images ii ON p.image_id=ii.image_id "
        "LEFT JOIN inspections i ON ii.inspection_id=i.inspection_id "
        "LEFT JOIN drones d ON i.drone_id=d.drone_id "
        "ORDER BY ir.created_at DESC, ir.report_id DESC" + suffix
    )


def dashboard_data() -> dict:
    counts = {}
    for name, table in {
        "inspections": "inspections", "images": "inspection_images",
        "predictions": "predictions", "reports": "inspection_reports",
        "models": "models", "datasets": "datasets",
    }.items():
        counts[name] = int(fetch_rows(f"SELECT COUNT(*) AS total FROM {table}")[0]["total"])
    avg = fetch_rows("SELECT ROUND(AVG(confidence),2) AS value FROM predictions")[0]["value"]
    critical = fetch_rows(
        "SELECT COUNT(*) AS total FROM inspection_reports WHERE intervention_priority='Critique'"
    )[0]["total"]
    priorities = fetch_rows(
        "SELECT intervention_priority AS label, COUNT(*) AS total FROM inspection_reports "
        "GROUP BY intervention_priority ORDER BY total DESC"
    )
    classes = fetch_rows(
        "SELECT dc.class_name AS label, COUNT(*) AS total FROM predictions p "
        "JOIN defect_classes dc ON p.predicted_class=dc.class_id "
        "GROUP BY dc.class_name ORDER BY total DESC"
    )
    models_usage = fetch_rows(
        "SELECT m.model_name AS label, COUNT(*) AS total FROM predictions p "
        "JOIN models m ON p.model_id=m.model_id GROUP BY m.model_name ORDER BY total DESC"
    )
    confidence_models = fetch_rows(
        "SELECT m.model_name AS label, ROUND(AVG(p.confidence),2) AS total "
        "FROM predictions p JOIN models m ON p.model_id=m.model_id "
        "GROUP BY m.model_name ORDER BY total DESC"
    )
    timeline = fetch_rows(
        "SELECT DATE(prediction_date) AS label, COUNT(*) AS total FROM predictions "
        "GROUP BY DATE(prediction_date) ORDER BY label"
    )
    counts.update({"confidence": float(avg or 0), "critical": int(critical)})
    return {"kpis": counts, "priorities": priorities, "classes": classes,
            "models_usage": models_usage, "confidence_models": confidence_models,
            "timeline": timeline}


def admin_data() -> dict:
    return {
        "users": fetch_rows(
            "SELECT user_id, full_name, email, role, is_active, created_at FROM users ORDER BY user_id"
        ),
        "models": fetch_rows(
            "SELECT model_id, model_name, model_type, input_size, accuracy, created_at "
            "FROM models ORDER BY model_id"
        ),
        "logs": fetch_rows(
            "SELECT l.log_id, l.action_date, l.action_type, l.action_description, "
            "u.full_name FROM logs l LEFT JOIN users u ON l.user_id=u.user_id "
            "ORDER BY l.action_date DESC, l.log_id DESC LIMIT 500"
        ),
    }


def create_user(full_name: str, email: str, role: str) -> int:
    full_name, email = full_name.strip(), email.strip().lower()
    if not full_name or "@" not in email or "." not in email:
        raise ValueError("Nom ou adresse e-mail invalide.")
    if role not in {"Administrateur", "Inspecteur", "Observateur"}:
        raise ValueError("Rôle invalide.")
    with transaction() as cursor:
        cursor.execute(
            "INSERT INTO users (full_name,email,password_hash,role,is_active) "
            "VALUES (%s,%s,NULL,%s,TRUE)", (full_name, email, role),
        )
        user_id = int(cursor.lastrowid)
        cursor.execute(
            "INSERT INTO logs (user_id,action_type,action_description) VALUES (%s,%s,%s)",
            (_application_user_id(cursor), "Création utilisateur Flask",
             f"Création du compte métier n°{user_id} ({email})."),
        )
    return user_id


def update_user(user_id: int, role: str, is_active: bool) -> None:
    if role not in {"Administrateur", "Inspecteur", "Observateur"}:
        raise ValueError("Rôle invalide.")
    with transaction() as cursor:
        cursor.execute(
            "UPDATE users SET role=%s,is_active=%s WHERE user_id=%s",
            (role, bool(is_active), int(user_id)),
        )
        if cursor.rowcount != 1:
            raise ValueError("Utilisateur introuvable.")
        cursor.execute(
            "INSERT INTO logs (user_id,action_type,action_description) VALUES (%s,%s,%s)",
            (_application_user_id(cursor), "Modification utilisateur Flask",
             f"Modification du compte métier n°{user_id}."),
        )


def _id(cursor, table: str, id_column: str, name_column: str, name: str) -> int:
    allowed = {
        ("models", "model_id", "model_name"),
        ("datasets", "dataset_id", "dataset_name"),
        ("defect_classes", "class_id", "class_name"),
    }
    if (table, id_column, name_column) not in allowed:
        raise ValueError("Référentiel non autorisé.")
    cursor.execute(
        f"SELECT {id_column} FROM {table} WHERE {name_column}=%s LIMIT 1", (name,)
    )
    row = cursor.fetchone()
    if not row:
        raise LookupError(f"Valeur absente de {table} : {name}")
    return int(row[0])


def _application_user_id(cursor):
    cursor.execute(
        "SELECT user_id FROM users WHERE is_active=TRUE "
        "ORDER BY CASE WHEN role='Administrateur' THEN 0 ELSE 1 END, user_id LIMIT 1"
    )
    row = cursor.fetchone()
    return int(row[0]) if row else None


def save_analysis(
    inspection_id: int, image: Image.Image, original_name: str,
    level_1: dict, level_2: list[dict],
) -> dict:
    safe_name = secure_filename(original_name) or "inspection.jpg"
    extension = Path(safe_name).suffix.lower() or ".jpg"
    filename = f"flask_inspection_{inspection_id}_{datetime.now():%Y%m%d_%H%M%S}_{uuid4().hex[:8]}{extension}"
    path = UPLOAD_DIR / filename
    image.convert("RGB").save(path)
    prediction_ids, report_ids = [], []
    try:
        with transaction() as cursor:
            dataset_name = "CODEBRIM" if level_2 else "Surface Crack Detection"
            dataset_id = _id(cursor, "datasets", "dataset_id", "dataset_name", dataset_name)
            cursor.execute(
                "INSERT INTO inspection_images "
                "(inspection_id,dataset_id,image_name,image_path) VALUES (%s,%s,%s,%s)",
                (inspection_id, dataset_id, filename, f"uploads/{filename}"),
            )
            image_id = int(cursor.lastrowid)
            for result in [level_1] + level_2:
                model_id = _id(cursor, "models", "model_id", "model_name", result["model_name"])
                class_id = _id(cursor, "defect_classes", "class_id", "class_name", result["class_name"])
                cursor.execute(
                    "INSERT INTO predictions (image_id,model_id,predicted_class,confidence) "
                    "VALUES (%s,%s,%s,%s)",
                    (image_id, model_id, class_id, round(result["confidence"] * 100, 2)),
                )
                prediction_id = int(cursor.lastrowid); prediction_ids.append(prediction_id)
                cursor.execute(
                    "INSERT INTO inspection_reports "
                    "(prediction_id,intervention_priority,recommendation) VALUES (%s,%s,%s)",
                    (prediction_id, result["priority"], result["recommendation"]),
                )
                report_ids.append(int(cursor.lastrowid))
            cursor.execute(
                "INSERT INTO logs (user_id,action_type,action_description) VALUES (%s,%s,%s)",
                (_application_user_id(cursor), "Prédiction Flask",
                 f"Image {image_id} analysée via Flask ; {len(prediction_ids)} prédiction(s)."),
            )
        return {"image_id": image_id, "prediction_ids": prediction_ids, "report_ids": report_ids}
    except Exception:
        path.unlink(missing_ok=True)
        raise


def import_inspections(rows: list[dict], source_name: str) -> int:
    allowed_types = {"Pont", "Toiture", "Pylône", "Bâtiment", "Autre"}
    allowed_statuses = {"Planifiée", "En cours", "Terminée", "Annulée"}
    required = {"inspection_date", "location", "infrastructure_type"}
    normalized = []
    for number, row in enumerate(rows, start=2):
        missing = [key for key in required if not str(row.get(key, "")).strip()]
        if missing:
            raise ValueError(f"Ligne {number} : champs requis absents : {', '.join(missing)}")
        try:
            date = datetime.fromisoformat(str(row["inspection_date"])[:10]).date()
        except ValueError as exc:
            raise ValueError(f"Ligne {number} : inspection_date doit être AAAA-MM-JJ.") from exc
        infrastructure = str(row["infrastructure_type"]).strip()
        status = str(row.get("status") or "Planifiée").strip()
        if infrastructure not in allowed_types:
            raise ValueError(f"Ligne {number} : type d'infrastructure invalide.")
        if status not in allowed_statuses:
            raise ValueError(f"Ligne {number} : statut invalide.")
        normalized.append((
            row.get("drone_id") or None, date, str(row["location"]).strip(), infrastructure,
            str(row.get("inspector_name") or "Import Flask").strip(),
            str(row.get("weather_conditions") or "Non renseignée").strip(), status,
            str(row.get("description") or "").strip() or None,
        ))
    with transaction() as cursor:
        cursor.execute("SELECT drone_id FROM drones ORDER BY drone_id LIMIT 1")
        default_drone = cursor.fetchone()
        if not default_drone:
            raise ValueError("Aucun drone n'est référencé dans la base.")
        values = [((item[0] or default_drone[0]), *item[1:]) for item in normalized]
        cursor.executemany(
            "INSERT INTO inspections "
            "(drone_id,inspection_date,location,infrastructure_type,inspector_name," 
            "weather_conditions,status,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", values,
        )
        cursor.execute(
            "INSERT INTO logs (user_id,action_type,action_description) VALUES (%s,%s,%s)",
            (_application_user_id(cursor), "Import inspections",
             f"{len(values)} inspection(s) importée(s) depuis {secure_filename(source_name)}."),
        )
    return len(normalized)
