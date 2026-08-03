"""
Import du référentiel d'inspections (CSV, XLSX ou JSON) vers la table `inspections`.

Répond à l'exigence du guide : « au moins un des trois types de fichiers proposés
est utilisé pour alimenter la base de données: csv, xlsx, json ».

Le format attendu correspond au dictionnaire de données de la section 5.3 du mémoire.
Colonnes obligatoires :
    drone_id, inspection_date, location, infrastructure_type,
    inspector_name, weather_conditions, status, description

Règles de contrôle appliquées avant insertion (traçabilité + conformité) :
    - toutes les colonnes obligatoires sont présentes
    - drone_id existe déjà dans la table `drones` (contrôle d'intégrité référentielle)
    - inspection_date est une date valide (format AAAA-MM-JJ)
    - infrastructure_type appartient à l'ENUM autorisé
    - status appartient à l'ENUM autorisé
    - inspector_name n'est pas vide (donnée personnelle minimisée : pas d'email/téléphone importé)

Chaque ligne rejetée est consignée avec sa raison, sans bloquer l'import des lignes
valides. Un rapport structuré est retourné pour affichage (Streamlit) et archivage.

Usage direct (hors app) :
    python import_referentiel.py sample_inspections_import.csv
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import mysql.connector
from shared_config import get_mysql_config

REQUIRED_COLUMNS = [
    "drone_id", "inspection_date", "location", "infrastructure_type",
    "inspector_name", "weather_conditions", "status", "description",
]

ALLOWED_INFRASTRUCTURE_TYPES = {"Pont", "Toiture", "Pylône", "Bâtiment", "Autre"}
ALLOWED_STATUSES = {"Planifiée", "En cours", "Terminée", "Annulée"}


def load_file(filepath: str) -> pd.DataFrame:
    """Charge un CSV, XLSX ou JSON en DataFrame selon l'extension."""
    ext = Path(filepath).suffix.lower()
    if ext == ".csv":
        return pd.read_csv(filepath)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(filepath)
    elif ext == ".json":
        return pd.read_json(filepath)
    else:
        raise ValueError(f"Format non supporté : {ext} (attendu : .csv, .xlsx ou .json)")


def validate_row(row: dict, valid_drone_ids: set) -> list:
    """Retourne la liste des erreurs de validation pour une ligne (vide = ligne valide)."""
    errors = []

    for col in REQUIRED_COLUMNS:
        if col not in row or pd.isna(row[col]) or str(row[col]).strip() == "":
            errors.append(f"colonne '{col}' manquante ou vide")

    if errors:
        return errors  # inutile de continuer si des colonnes de base manquent

    if int(row["drone_id"]) not in valid_drone_ids:
        errors.append(f"drone_id {row['drone_id']} introuvable dans la table drones")

    try:
        datetime.strptime(str(row["inspection_date"]), "%Y-%m-%d")
    except ValueError:
        errors.append(f"inspection_date invalide : '{row['inspection_date']}' (attendu AAAA-MM-JJ)")

    if row["infrastructure_type"] not in ALLOWED_INFRASTRUCTURE_TYPES:
        errors.append(f"infrastructure_type invalide : '{row['infrastructure_type']}'")

    if row["status"] not in ALLOWED_STATUSES:
        errors.append(f"status invalide : '{row['status']}'")

    return errors


def import_referentiel(filepath: str) -> dict:
    """
    Importe un fichier de référentiel d'inspections vers la base.

    Retourne un rapport structuré :
        {
            "filepath": ..., "total_rows": ..., "inserted": ...,
            "rejected": ..., "errors": [{"row": i, "reasons": [...]}]
        }
    """
    df = load_file(filepath)

    conn = mysql.connector.connect(**get_mysql_config())
    cursor = conn.cursor()

    cursor.execute("SELECT drone_id FROM drones")
    valid_drone_ids = {r[0] for r in cursor.fetchall()}

    inserted_rows = []
    rejected_rows = []

    for i, row in df.iterrows():
        row_dict = row.to_dict()
        errors = validate_row(row_dict, valid_drone_ids)

        if errors:
            rejected_rows.append({"row": int(i) + 1, "reasons": errors})
            continue

        cursor.execute(
            """INSERT INTO inspections
               (drone_id, inspection_date, location, infrastructure_type,
                inspector_name, weather_conditions, status, description)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                int(row_dict["drone_id"]),
                row_dict["inspection_date"],
                row_dict["location"],
                row_dict["infrastructure_type"],
                row_dict["inspector_name"],
                row_dict["weather_conditions"],
                row_dict["status"],
                row_dict["description"],
            ),
        )
        inserted_rows.append(int(i) + 1)

    conn.commit()
    cursor.close()
    conn.close()

    report = {
        "filepath": str(filepath),
        "imported_at": datetime.now().isoformat(timespec="seconds"),
        "total_rows": len(df),
        "inserted": len(inserted_rows),
        "rejected": len(rejected_rows),
        "errors": rejected_rows,
    }

    # Trace du chargement : un rapport JSON horodaté à côté du fichier importé,
    # pour audit — répond à l'exigence de traçabilité du guide (section 5.1).
    report_path = Path(filepath).with_suffix(".import_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    report["report_path"] = str(report_path)

    return report


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python import_referentiel.py <fichier.csv|.xlsx|.json>")
        sys.exit(1)

    result = import_referentiel(sys.argv[1])
    print(f"\nFichier : {result['filepath']}")
    print(f"Lignes totales : {result['total_rows']}")
    print(f"Insérées : {result['inserted']}")
    print(f"Rejetées : {result['rejected']}")
    if result["errors"]:
        print("\nDétail des rejets :")
        for err in result["errors"]:
            print(f"  Ligne {err['row']} : {', '.join(err['reasons'])}")
    print(f"\nRapport sauvegardé : {result['report_path']}")
