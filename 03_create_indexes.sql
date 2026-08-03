-- Étape 4a — Création des index d'optimisation
--
-- Cible les deux points identifiés par EXPLAIN ANALYZE dans benchmark_before.json :
--   - le filtre WHERE intervention_priority = 'Critique' (table inspection_reports)
--   - le tri ORDER BY prediction_date DESC (table predictions)
--
-- À exécuter UNE SEULE FOIS avant de relancer le benchmark (étape 4b).

USE drone_inspection_ai;

CREATE INDEX idx_reports_priority
    ON inspection_reports (intervention_priority);

CREATE INDEX idx_predictions_date
    ON predictions (prediction_date);

-- Vérification : les deux index doivent apparaître ci-dessous
SHOW INDEX FROM inspection_reports WHERE Key_name = 'idx_reports_priority';
SHOW INDEX FROM predictions WHERE Key_name = 'idx_predictions_date';
