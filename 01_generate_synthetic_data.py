"""
Étape 2 — Génération de données synthétiques pour le benchmark SQL.

Peuple inspection_images, predictions et inspection_reports avec un volume
réaliste, en réutilisant les inspections/drones/datasets/modèles/classes déjà
présents dans la base (créés par le script de schéma initial).

Usage :
    pip install mysql-connector-python
    python 01_generate_synthetic_data.py

Modifie les paramètres de connexion et N_ROWS ci-dessous avant de lancer.
"""

import random
import time
import mysql.connector
from shared_config import get_mysql_config

# ------------------------------------------------------------------
# Paramètres à adapter
# ------------------------------------------------------------------
DB_CONFIG = get_mysql_config()

N_ROWS = 20000  # nombre d'images / prédictions / rapports à générer
BATCH_SIZE = 1000

INFRASTRUCTURE_TYPES = ["Pont", "Toiture", "Pylône", "Bâtiment", "Autre"]
WEATHER = ["Ciel dégagé", "Nuageux", "Pluie légère", "Vent modéré"]
STATUSES = ["Planifiée", "En cours", "Terminée", "Annulée"]
PRIORITIES = ["Faible", "Moyenne", "Élevée", "Critique"]


def get_reference_ids(cursor):
    """Récupère les IDs existants nécessaires aux clés étrangères."""
    cursor.execute("SELECT drone_id FROM drones")
    drone_ids = [r[0] for r in cursor.fetchall()]
    if not drone_ids:
        raise RuntimeError("Aucun drone trouvé — insère au moins un drone avant de lancer ce script.")

    cursor.execute("SELECT dataset_id FROM datasets")
    dataset_ids = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT model_id FROM models")
    model_ids = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT class_id FROM defect_classes")
    class_ids = [r[0] for r in cursor.fetchall()]

    if not (dataset_ids and model_ids and class_ids):
        raise RuntimeError("datasets / models / defect_classes doivent déjà contenir des lignes.")

    return drone_ids, dataset_ids, model_ids, class_ids


def generate_inspections(cursor, conn, drone_ids, n=200):
    """Crée n inspections synthétiques (les images s'y rattacheront)."""
    rows = []
    for i in range(n):
        rows.append((
            random.choice(drone_ids),
            f"2026-{random.randint(1,7):02d}-{random.randint(1,28):02d}",
            f"Site synthétique {i}",
            random.choice(INFRASTRUCTURE_TYPES),
            "Camelia Cherchem",
            random.choice(WEATHER),
            random.choice(STATUSES),
            "Inspection générée pour le benchmark SQL.",
        ))

    cursor.executemany(
        """INSERT INTO inspections
           (drone_id, inspection_date, location, infrastructure_type,
            inspector_name, weather_conditions, status, description)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        rows,
    )
    conn.commit()

    cursor.execute("SELECT inspection_id FROM inspections")
    return [r[0] for r in cursor.fetchall()]


def generate_images_predictions_reports(cursor, conn, inspection_ids, dataset_ids,
                                         model_ids, class_ids, n_rows, batch_size):
    """Génère n_rows images, chacune avec une prédiction et un rapport associés."""
    inserted = 0
    t0 = time.time()

    while inserted < n_rows:
        batch = min(batch_size, n_rows - inserted)

        image_rows = []
        for i in range(batch):
            idx = inserted + i
            image_rows.append((
                random.choice(dataset_ids),
                random.choice(inspection_ids),
                f"synthetic_image_{idx}.jpg",
                f"data/synthetic/synthetic_image_{idx}.jpg",
            ))

        cursor.executemany(
            """INSERT INTO inspection_images
               (dataset_id, inspection_id, image_name, image_path)
               VALUES (%s, %s, %s, %s)""",
            image_rows,
        )
        conn.commit()

        # Récupère les image_id qu'on vient d'insérer (les derniers `batch`)
        cursor.execute(
            "SELECT image_id FROM inspection_images ORDER BY image_id DESC LIMIT %s",
            (batch,),
        )
        new_image_ids = [r[0] for r in cursor.fetchall()][::-1]

        prediction_rows = []
        for image_id in new_image_ids:
            prediction_rows.append((
                image_id,
                random.choice(model_ids),
                random.choice(class_ids),
                round(random.uniform(60.0, 99.9), 2),
            ))

        cursor.executemany(
            """INSERT INTO predictions
               (image_id, model_id, predicted_class, confidence)
               VALUES (%s, %s, %s, %s)""",
            prediction_rows,
        )
        conn.commit()

        cursor.execute(
            "SELECT prediction_id FROM predictions ORDER BY prediction_id DESC LIMIT %s",
            (batch,),
        )
        new_prediction_ids = [r[0] for r in cursor.fetchall()][::-1]

        report_rows = []
        for prediction_id in new_prediction_ids:
            report_rows.append((
                prediction_id,
                random.choice(PRIORITIES),
                "Rapport généré automatiquement pour le benchmark SQL.",
            ))

        cursor.executemany(
            """INSERT INTO inspection_reports
               (prediction_id, intervention_priority, recommendation)
               VALUES (%s, %s, %s)""",
            report_rows,
        )
        conn.commit()

        inserted += batch
        elapsed = time.time() - t0
        print(f"  {inserted}/{n_rows} lignes insérées ({elapsed:.1f}s écoulées)")

    print(f"Terminé : {n_rows} images/prédictions/rapports générés en {time.time() - t0:.1f}s")


def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("Récupération des IDs de référence...")
    drone_ids, dataset_ids, model_ids, class_ids = get_reference_ids(cursor)

    print("Génération de 200 inspections synthétiques...")
    inspection_ids = generate_inspections(cursor, conn, drone_ids, n=200)

    print(f"Génération de {N_ROWS} images / prédictions / rapports...")
    generate_images_predictions_reports(
        cursor, conn, inspection_ids, dataset_ids, model_ids, class_ids,
        n_rows=N_ROWS, batch_size=BATCH_SIZE,
    )

    cursor.close()
    conn.close()
    print("Base peuplée avec succès. Passe maintenant au script de benchmark.")


if __name__ == "__main__":
    main()
