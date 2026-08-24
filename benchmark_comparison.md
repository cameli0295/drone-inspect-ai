# Benchmark SQL — Comparaison avant/après index

Requête : historique (jointure 6 tables, filtre `intervention_priority`, tri `prediction_date`)

La première exécution (gain de 2,1×) s'était révélée instable à cause d'un mauvais volume de test ; ce fichier reflète la mesure finale reproductible après correction.

Volume : 4934 lignes retournées sur 20 029 prédictions générées

| Métrique | Avant index | Après index | Gain |
|---|---|---|---|
| Médiane | 960.4 ms | 274.4 ms | 3.5x |
| P95 | 1023.1 ms | 304.8 ms | 3.4x |
