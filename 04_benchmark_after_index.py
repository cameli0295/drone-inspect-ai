"""
Étape 4b — Benchmark APRÈS optimisation, puis comparaison finale.

Chronomètre la même requête "historique" (identique à
02_benchmark_before_index.py) APRÈS création des index de
03_create_indexes.sql, puis génère un tableau comparatif
avant/après prêt à coller dans le mémoire.

Prérequis : avoir exécuté 03_create_indexes.sql avant de lancer ce script.

Usage :
    python 04_benchmark_after_index.py
"""

import json
import statistics
import time

import mysql.connector
from shared_config import get_mysql_config  # même import que le script "avant"

N_RUNS = 30
WARMUP_RUNS = 3

# Requête strictement identique à celle du benchmark "avant" —
# ne change rien ici, sinon la comparaison n'est plus valide.
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
    cursor.execute("EXPLAIN ANALYZE " + HISTORIQUE_QUERY)
    return "\n".join(row[0] for row in cursor.fetchall())


def run_timed(cursor, n_runs):
    times_ms = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        cursor.execute(HISTORIQUE_QUERY)
        cursor.fetchall()
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


def print_comparison_table(before, after):
    def gain(b, a):
        return f"{b / a:.1f}x" if a > 0 else "n/a"

    print("\n" + "=" * 60)
    print("COMPARAISON AVANT / APRÈS INDEX")
    print("=" * 60)
    print(f"{'Métrique':<12} {'Avant':>12} {'Après':>12} {'Gain':>8}")
    for key, label in [("median_ms", "Médiane"), ("p95_ms", "P95"),
                        ("mean_ms", "Moyenne"), ("min_ms", "Min"), ("max_ms", "Max")]:
        b, a = before["stats"][key], after["stats"][key]
        print(f"{label:<12} {b:>10.1f}ms {a:>10.1f}ms {gain(b, a):>8}")
    print("=" * 60)


def main():
    conn = mysql.connector.connect(**get_mysql_config())
    cursor = conn.cursor()

    print("Chronométrage de la requête historique (état APRÈS index)...")
    run_timed(cursor, WARMUP_RUNS)
    times_ms = run_timed(cursor, N_RUNS)
    stats = summarize(times_ms)
    print(f"  Médiane : {stats['median_ms']} ms | P95 : {stats['p95_ms']} ms")

    print("\nCapture du plan d'exécution (EXPLAIN ANALYZE)...")
    explain_output = capture_explain(cursor)
    print(explain_output)

    cursor.execute(HISTORIQUE_QUERY)
    row_count = len(cursor.fetchall())

    after_result = {
        "phase": "apres_index",
        "row_count": row_count,
        "stats": stats,
        "raw_times_ms": times_ms,
        "explain_analyze": explain_output,
    }

    with open("benchmark_after.json", "w", encoding="utf-8") as f:
        json.dump(after_result, f, ensure_ascii=False, indent=2)
    print("\nRésultats sauvegardés dans benchmark_after.json")

    # Comparaison avec le benchmark "avant" s'il existe
    try:
        with open("benchmark_before.json", "r", encoding="utf-8") as f:
            before_result = json.load(f)
        print_comparison_table(before_result, after_result)

        with open("benchmark_comparison.md", "w", encoding="utf-8") as f:
            f.write("# Benchmark SQL — Comparaison avant/après index\n\n")
            f.write(f"Requête : historique (jointure 6 tables, filtre `intervention_priority`, ")
            f.write(f"tri `prediction_date`)\n\n")
            f.write(f"Volume : {before_result['row_count']} lignes retournées sur "
                    f"20 029 prédictions générées\n\n")
            f.write("| Métrique | Avant index | Après index | Gain |\n")
            f.write("|---|---|---|---|\n")
            for key, label in [("median_ms", "Médiane"), ("p95_ms", "P95")]:
                b, a = before_result["stats"][key], after_result["stats"][key]
                f.write(f"| {label} | {b:.1f} ms | {a:.1f} ms | {b/a:.1f}x |\n")
        print("\nTableau markdown prêt pour le mémoire : benchmark_comparison.md")
    except FileNotFoundError:
        print("\n(benchmark_before.json introuvable — comparaison non générée)")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
