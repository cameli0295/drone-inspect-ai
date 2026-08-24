-- Données de démonstration anonymisées pour DroneInspect AI.
-- Aucun enregistrement opérationnel ou personnel de la base locale n'est exporté.
USE drone_inspection_ai;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE logs;
TRUNCATE TABLE inspection_reports;
TRUNCATE TABLE predictions;
TRUNCATE TABLE inspection_images;
TRUNCATE TABLE inspections;
TRUNCATE TABLE models;
TRUNCATE TABLE defect_classes;
TRUNCATE TABLE drones;
TRUNCATE TABLE datasets;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO datasets
  (dataset_id, dataset_name, description, total_images, source)
VALUES
  (1, 'Surface Crack Detection', 'Dataset de classification binaire des fissures', 40000, 'https://www.kaggle.com/datasets/arunrk7/surface-crack-detection'),
  (2, 'CODEBRIM', 'Dataset multi-étiquette des défauts du béton', 7729, 'https://zenodo.org/record/2620293');

INSERT INTO defect_classes (class_id, class_name, severity, description) VALUES
  (1, 'No Crack', 'Faible', 'Aucune fissure détectée'),
  (2, 'Crack', 'Moyenne', 'Présence de fissures sur la surface'),
  (3, 'Corrosion', 'Élevée', 'Corrosion des éléments métalliques'),
  (4, 'Efflorescence', 'Faible', 'Dépôts blanchâtres dus aux sels minéraux'),
  (5, 'Spallation', 'Critique', 'Éclatement ou détachement du béton'),
  (6, 'Exposed Rebar', 'Critique', 'Armatures métalliques visibles'),
  (7, 'Honeycombing', 'Élevée', 'Présence de nids de gravier dans le béton');

INSERT INTO drones
  (drone_id, drone_name, drone_model, camera_resolution, max_flight_time, description)
VALUES
  (1, 'DroneInspect-Demo', 'Drone de démonstration', '20 MP', '45 minutes', 'Référentiel anonymisé pour les tests locaux.');

INSERT INTO models
  (model_id, model_name, model_type, dataset_id, task_type, input_size, classes_count, model_path, accuracy, description)
VALUES
  (1, 'MobileNetV2', 'CNN Transfer Learning', 1, 'Classification binaire', '300x300x3', 2, 'models/MobileNetV2_archive_structure_commente.keras', 99.87, 'Détection binaire fissure / absence de fissure.'),
  (2, 'EfficientNetB3', 'CNN Transfer Learning', 2, 'Classification multiclasses', '300x300x3', 6, 'models/efficientnetb3_concrete_defects_corrige.keras', NULL, 'Classification multi-étiquette des défauts du béton.');

-- Compte applicatif de démonstration documenté dans le README ; à changer immédiatement.
INSERT INTO users
  (user_id, full_name, email, password_hash, role, is_active)
VALUES
  (1, 'Administrateur Démo', 'admin.demo@example.invalid', 'b6a1d1be6af2827fcf17d2cb7e2565a6ea88a415dd399bca65be4e14dcff62ce', 'Administrateur', TRUE);

INSERT INTO inspections
  (inspection_id, drone_id, inspection_date, location, infrastructure_type, inspector_name, weather_conditions, status, description)
VALUES
  (1, 1, '2026-08-01', 'Ouvrage de démonstration', 'Pont', 'Inspecteur Démo', 'Temps clair', 'Planifiée', 'Donnée fictive fournie uniquement pour valider les interfaces.');
