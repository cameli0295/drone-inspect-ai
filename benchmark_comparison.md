# Benchmark SQL — Comparaison avant/après index

Requête : historique (jointure 6 tables, filtre `intervention_priority`, tri `prediction_date`)

Volume : 4932 lignes retournées sur 20 029 prédictions générées

| Métrique | Avant index | Après index | Gain |
|---|---|---|---|
| Médiane | 960.4 ms | 454.4 ms | 2.1x |
| P95 | 1023.1 ms | 643.7 ms | 1.6x |
