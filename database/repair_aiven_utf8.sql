-- DroneInspect AI - réparation ponctuelle des données déjà corrompues sur Aiven.
-- NE PAS EXÉCUTER avant validation, sauvegarde et fenêtre de maintenance.
-- À exécuter UNE SEULE FOIS avec un client configuré en UTF-8.

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Contrôles avant modification.
SELECT user_id, full_name, HEX(full_name) FROM users WHERE full_name LIKE '%?%';
SELECT inspection_id, location, inspector_name FROM inspections
WHERE CONCAT_WS('', location, infrastructure_type, inspector_name,
                weather_conditions, status, description) LIKE '%?%';

-- Les ALTER TABLE provoquent un commit implicite dans MySQL. On élargit d'abord
-- les ENUM pour accepter simultanément les anciennes et les nouvelles valeurs.
ALTER TABLE inspections
  MODIFY infrastructure_type ENUM(
    'Pont','Toiture','Pyl??ne','B??timent','Pylône','Bâtiment','Autre'
  ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  MODIFY status ENUM(
    'Planifi??e','Planifiée','En cours','Termin??e','Terminée','Annul??e','Annulée'
  ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Planifi??e';

START TRANSACTION;

-- users
UPDATE users SET full_name = 'Administrateur Démo'
WHERE full_name = 'Administrateur D?mo';

-- inspections : valeurs structurées et fragments présents dans les données.
UPDATE inspections SET infrastructure_type = 'Pylône'
WHERE infrastructure_type = 'Pyl??ne';
UPDATE inspections SET infrastructure_type = 'Bâtiment'
WHERE infrastructure_type = 'B??timent';
UPDATE inspections SET status = 'Planifiée' WHERE status = 'Planifi??e';
UPDATE inspections SET status = 'Terminée' WHERE status = 'Termin??e';
UPDATE inspections SET status = 'Annulée' WHERE status = 'Annul??e';
UPDATE inspections SET inspector_name = 'Inspecteur Démo'
WHERE inspector_name = 'Inspecteur D?mo';
UPDATE inspections SET location = REPLACE(location, 'B??timent', 'Bâtiment');
UPDATE inspections SET location = REPLACE(location, 'Pyl??ne', 'Pylône');
UPDATE inspections SET location = REPLACE(location, 'entrep??t', 'entrepôt');
UPDATE inspections SET location = REPLACE(location, 'd??monstration', 'démonstration');
UPDATE inspections SET location = REPLACE(location, 'synth??tique', 'synthétique');
UPDATE inspections SET location = REPLACE(location, '??le-de-France', 'Île-de-France');
UPDATE inspections SET weather_conditions = REPLACE(weather_conditions, 'd??gag??', 'dégagé');
UPDATE inspections SET weather_conditions = REPLACE(weather_conditions, 'l??g??re', 'légère');
UPDATE inspections SET weather_conditions = REPLACE(weather_conditions, 'mod??r??', 'modéré');
UPDATE inspections SET description = REPLACE(description, 'd??monstration', 'démonstration');
UPDATE inspections SET description = REPLACE(description, 'th??se', 'thèse');
UPDATE inspections SET description = REPLACE(description, 'g??n??r??e', 'générée');
UPDATE inspections SET description = REPLACE(description, 'Contr??le', 'Contrôle');
UPDATE inspections SET description = REPLACE(description, 'contr??le', 'contrôle');
UPDATE inspections SET description = REPLACE(description, 'p??riodique', 'périodique');
UPDATE inspections SET description = REPLACE(description, 'fa??ade', 'façade');
UPDATE inspections SET description = REPLACE(description, 'b??ton', 'béton');
UPDATE inspections SET description = REPLACE(description, 'suite ??', 'suite à');
UPDATE inspections SET description = REPLACE(description, 'd???inspection', 'd''inspection');
UPDATE inspections SET description = REPLACE(description, 'd???un', 'd''un');
UPDATE inspections SET description = REPLACE(description, 'r??alis??e', 'réalisée');
UPDATE inspections SET description = REPLACE(description, 'l?????tat', 'l''état');
UPDATE inspections SET description = REPLACE(description, ' ?? partir', ' à partir');
UPDATE inspections SET description = REPLACE(description, 'd???images', 'd''images');
UPDATE inspections SET description = REPLACE(description, 'captur??es', 'capturées');
UPDATE inspections SET description = REPLACE(description, 'pyl??ne', 'pylône');

-- datasets
UPDATE datasets SET description = REPLACE(description, 'd??fauts', 'défauts');
UPDATE datasets SET description = REPLACE(description, 'b??ton', 'béton');

-- defect_classes
UPDATE defect_classes SET description = REPLACE(description, 'd??tect??e', 'détectée');
UPDATE defect_classes SET description = REPLACE(description, 'Pr??sence', 'Présence');
UPDATE defect_classes SET description = REPLACE(description, 'pr??sence', 'présence');
UPDATE defect_classes SET description = REPLACE(description, '??l??ments', 'éléments');
UPDATE defect_classes SET description = REPLACE(description, 'm??talliques', 'métalliques');
UPDATE defect_classes SET description = REPLACE(description, 'D??p??ts', 'Dépôts');
UPDATE defect_classes SET description = REPLACE(description, 'blanch??tres', 'blanchâtres');
UPDATE defect_classes SET description = REPLACE(description, 'min??raux', 'minéraux');
UPDATE defect_classes SET description = REPLACE(description, '??clatement', 'Éclatement');
UPDATE defect_classes SET description = REPLACE(description, 'd??tachement', 'détachement');
UPDATE defect_classes SET description = REPLACE(description, 'b??ton', 'béton');

-- drones
UPDATE drones SET description = REPLACE(description, 'utilis??', 'utilisé');

-- inspection_reports
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'Pr??voir', 'Prévoir');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'Contr??le', 'Contrôle');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'contr??le', 'contrôle');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'a ??t??', 'a été');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'd??tect??e', 'détectée');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'd??tect??', 'détecté');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'd??faut', 'défaut');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'lanc??e', 'lancée');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'recommand??e', 'recommandée');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'S??curiser', 'Sécuriser');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'r??paration', 'réparation');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'b??ton', 'béton');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'd??t??rior??', 'détérioré');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'pr??sentant', 'présentant');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'compl??mentaire', 'complémentaire');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'd??taill??e', 'détaillée');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'lanc??', 'lancé');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'humidit??', 'humidité');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'l''??volution', 'l''évolution');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'd??p??ts', 'dépôts');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'n??cessaire', 'nécessaire');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'imm??diate', 'immédiate');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, 'R??parer', 'Réparer');
UPDATE inspection_reports SET recommendation = REPLACE(recommendation, '??clatement', 'éclatement');

-- logs
UPDATE logs SET action_type = REPLACE(action_type, 'Pr??diction', 'Prédiction');
UPDATE logs SET action_type = REPLACE(action_type, 'Cr??ation', 'Création');
UPDATE logs SET action_type = REPLACE(action_type, 'mod??les', 'modèles');
UPDATE logs SET action_description = REPLACE(action_description, 'Cr??ation', 'Création');
UPDATE logs SET action_description = REPLACE(action_description, 'Ex??cution', 'Exécution');
UPDATE logs SET action_description = REPLACE(action_description, 'G??n??ration', 'Génération');
UPDATE logs SET action_description = REPLACE(action_description, 'pr??diction', 'prédiction');
UPDATE logs SET action_description = REPLACE(action_description, 'mod??les', 'modèles');
UPDATE logs SET action_description = REPLACE(action_description, 'd??monstration', 'démonstration');
UPDATE logs SET action_description = REPLACE(action_description, 'd???inspection', 'd''inspection');
UPDATE logs SET action_description = REPLACE(action_description, 'ins??r??', 'inséré');
UPDATE logs SET action_description = REPLACE(action_description, 'import??e', 'importée');
UPDATE logs SET action_description = REPLACE(action_description, 'analys??e', 'analysée');
UPDATE logs SET action_description = REPLACE(action_description, '?? deux niveaux', 'à deux niveaux');
UPDATE logs SET action_description = REPLACE(action_description, 'n??', 'n°');
UPDATE logs SET action_description = REPLACE(action_description, 'r??sultat', 'résultat');
UPDATE logs SET action_description = REPLACE(action_description, 'enregistr??e', 'enregistrée');
UPDATE logs SET action_description = REPLACE(action_description, 'enregistr??', 'enregistré');
UPDATE logs SET action_description = REPLACE(action_description, ' ?? ', ' à ');

-- models
UPDATE models SET description = REPLACE(description, 'Mod??le', 'Modèle');
UPDATE models SET description = REPLACE(description, 'utilis??', 'utilisé');
UPDATE models SET description = REPLACE(description, 'd??tecter', 'détecter');
UPDATE models SET description = REPLACE(description, 'pr??sence', 'présence');
UPDATE models SET description = REPLACE(description, 'l???absence', 'l''absence');
UPDATE models SET description = REPLACE(description, ' ?? partir', ' à partir');
UPDATE models SET description = REPLACE(description, 'd??fauts', 'défauts');

COMMIT;

-- Refermer les ENUM sur les seules valeurs correctes. DDL = commit implicite.
ALTER TABLE inspections
  MODIFY infrastructure_type ENUM(
    'Pont','Toiture','Pylône','Bâtiment','Autre'
  ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  MODIFY status ENUM(
    'Planifiée','En cours','Terminée','Annulée'
  ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Planifiée';

-- Vérifications finales : cette requête doit retourner zéro ligne.
SELECT 'datasets.description' AS source, COUNT(*) AS remaining FROM datasets WHERE description LIKE '%?%'
UNION ALL SELECT 'defect_classes.description', COUNT(*) FROM defect_classes WHERE description LIKE '%?%'
UNION ALL SELECT 'drones.description', COUNT(*) FROM drones WHERE description LIKE '%?%'
UNION ALL SELECT 'inspection_reports.recommendation', COUNT(*) FROM inspection_reports WHERE recommendation LIKE '%?%'
UNION ALL SELECT 'inspections.location', COUNT(*) FROM inspections WHERE location LIKE '%?%'
UNION ALL SELECT 'inspections.infrastructure_type', COUNT(*) FROM inspections WHERE infrastructure_type LIKE '%?%'
UNION ALL SELECT 'inspections.inspector_name', COUNT(*) FROM inspections WHERE inspector_name LIKE '%?%'
UNION ALL SELECT 'inspections.weather_conditions', COUNT(*) FROM inspections WHERE weather_conditions LIKE '%?%'
UNION ALL SELECT 'inspections.status', COUNT(*) FROM inspections WHERE status LIKE '%?%'
UNION ALL SELECT 'inspections.description', COUNT(*) FROM inspections WHERE description LIKE '%?%'
UNION ALL SELECT 'logs.action_type', COUNT(*) FROM logs WHERE action_type LIKE '%?%'
UNION ALL SELECT 'logs.action_description', COUNT(*) FROM logs WHERE action_description LIKE '%?%'
UNION ALL SELECT 'models.description', COUNT(*) FROM models WHERE description LIKE '%?%'
UNION ALL SELECT 'users.full_name', COUNT(*) FROM users WHERE full_name LIKE '%?%';

SELECT full_name FROM users WHERE user_id = 1;
SELECT inspection_id, location FROM inspections WHERE location LIKE '%Pantin%';
