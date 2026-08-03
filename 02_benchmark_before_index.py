"""
Étape 3 — Benchmark AVANT optimisation.

Chronomètre la requête "historique" représentative de l'application
(jointure sur 6 tables, filtre sur intervention_priority, tri sur
prediction_date) AVANT création d'index supplémentaires.

Sauvegarde les résultats dans benchmark_before.json pour comparaison
ultérieure avec la version indexée (étape 4).

Usage :
    python 02_benchmark_before_index.py
"""

import json
import statistics
import time

import mysql.connector
from shared_config import get_mysql_config  # réutilise la configuration .env existante

N_RUNS = 30
WARMUP_RUNS = 3  # runs "à chaud" ignorés pour laisser le buffer pool InnoDB se remplir

HISTORIQUE_QUERY = """
SELECT
    i.inspection_id, i.location, i.infrastructure_type, i.inspection_date,
    img.image_id, img.image_name,
    p.prediction_id, p.confidence, p.prediction_date,
    dc.class_name, dc.severity,
    m.model_name,
    r.report_id, r.intervention_priority, r.recommendation
FROM inspections i
JOIN inspection_images img   ON img.inspection_id = i.inspection_id
JOIN predictions p           ON p.image_id = img.image_id
JOIN models m                ON m.model_id = p.model_id
JOIN defect_classes dc       ON dc.class_id = p.predicted_class
JOIN inspection_reports r    ON r.prediction_id = p.prediction_id
WHERE r.intervention_priority = 'Critique'
ORDER BY p.prediction_date DESC
"""


def capture_explain(cursor):
    """Capture le plan d'exécution réel (EXPLAIN ANALYZE) pour le mémoire."""
    cursor.execute("EXPLAIN ANALYZE " + HISTORIQUE_QUERY)
    return "\n".join(row[0] for row in cursor.fetchall())


def run_timed(cursor, n_runs):
    """Exécute la requête n_runs fois, renvoie la liste des temps en ms."""
    times_ms = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        cursor.execute(HISTORIQUE_QUERY)
        cursor.fetchall()  # force la lecture complète du résultat
        elapsed_ms = (time.perf_counter() - t0) * 1000
        times_ms.append(elapsed_ms)
    return times_ms


def summarize(times_ms):
    sorted_times = sorted(times_ms)
    p95_index = int(len(sorted_times) * 0.95) - 1
    return {
        "n_runs": len(times_ms),
        "median_ms": round(statistics.median(times_ms), 3),
        "mean_ms": round(statistics.mean(times_ms), 3),
        "p95_ms": round(sorted_times[max(p95_index, 0)], 3),
        "min_ms": round(min(times_ms), 3),
        "max_ms": round(max(times_ms), 3),
    }


def main():
    conn = mysql.connector.connect(**get_mysql_config())
    cursor = conn.cursor()

    print(f"Nombre de lignes retournées par la requête historique :")
    cursor.execute(HISTORIQUE_QUERY)
    row_count = len(cursor.fetchall())
    print(f"  -> {row_count} lignes")

    print(f"\nWarm-up ({WARMUP_RUNS} exécutions ignorées)...")
    run_timed(cursor, WARMUP_RUNS)

    print(f"Chronométrage de {N_RUNS} exécutions (état AVANT index)...")
    times_ms = run_timed(cursor, N_RUNS)
    stats = summarize(times_ms)
    print(f"  Médiane : {stats['median_ms']} ms | P95 : {stats['p95_ms']} ms")

    print("\nCapture du plan d'exécution (EXPLAIN ANALYZE)...")
    explain_output = capture_explain(cursor)
    print(explain_output)

    result = {
        "phase": "avant_index",
        "row_count": row_count,
        "stats": stats,
        "raw_times_ms": times_ms,
        "explain_analyze": explain_output,
    }

    with open("benchmark_before.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\nRésultats sauvegardés dans benchmark_before.json")
    print("Passe maintenant à la création des index (étape 4).")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
