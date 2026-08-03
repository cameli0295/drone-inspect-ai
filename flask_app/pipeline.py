"""Pipeline Keras utilisé par l'application Flask.

Les paramètres de prétraitement, seuils et libellés sont alignés sur app.py.
Les modèles existants sont chargés une seule fois par processus Flask.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from time import perf_counter

import numpy as np
from PIL import Image
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.models import load_model

from shared_config import BASE_DIR


MODEL_DIR = BASE_DIR / "models"
MOBILENET_PATH = MODEL_DIR / "MobileNetV2_archive_structure_commente.keras"
EFFICIENTNET_PATH = MODEL_DIR / "efficientnetb3_concrete_defects_corrige.keras"
CRACK_THRESHOLD = 0.50

LABELS = [
    "Background", "Crack", "Spallation", "Efflorescence",
    "ExposedBars", "CorrosionStain",
]
THRESHOLDS = {
    "Background": 0.55, "Crack": 0.55, "Spallation": 0.60,
    "Efflorescence": 0.30, "ExposedBars": 0.65, "CorrosionStain": 0.35,
}
MAPPING = {
    "Background": ("No Crack", "Faible", "Aucun défaut structurel significatif détecté."),
    "Crack": ("Crack", "Moyenne", "Programmer une inspection de contrôle afin de surveiller l'évolution de la fissure."),
    "Spallation": ("Spallation", "Critique", "Sécuriser la zone et programmer rapidement une réparation du béton détérioré."),
    "Efflorescence": ("Efflorescence", "Faible", "Contrôler l'origine de l'humidité et surveiller l'évolution des dépôts."),
    "ExposedBars": ("Exposed Rebar", "Critique", "Réaliser une inspection structurelle urgente des armatures apparentes."),
    "CorrosionStain": ("Corrosion", "Élevée", "Prévoir rapidement un diagnostic et un traitement anticorrosion."),
}


@lru_cache(maxsize=1)
def mobilenet():
    if not MOBILENET_PATH.exists():
        raise FileNotFoundError(f"Modèle introuvable : {MOBILENET_PATH}")
    return load_model(MOBILENET_PATH, compile=False)


@lru_cache(maxsize=1)
def efficientnet():
    if not EFFICIENTNET_PATH.exists():
        raise FileNotFoundError(f"Modèle introuvable : {EFFICIENTNET_PATH}")
    return load_model(EFFICIENTNET_PATH, compile=False)


def predict_level_1(image: Image.Image) -> dict:
    batch = np.expand_dims(np.asarray(image.resize((300, 300)), dtype=np.float32), 0)
    started = perf_counter()
    output = np.asarray(mobilenet().predict(batch, verbose=0)).reshape(-1)
    elapsed = perf_counter() - started
    probability = float(output[0] if output.size == 1 else output[1])
    crack = probability >= CRACK_THRESHOLD
    return {
        "model_name": "MobileNetV2",
        "class_name": "Crack" if crack else "No Crack",
        "confidence": probability if crack else 1.0 - probability,
        "raw_probability": probability,
        "inference_time": elapsed,
        "priority": "Moyenne" if crack else "Faible",
        "recommendation": (
            "Une fissure a été détectée ; le niveau 2 est lancé."
            if crack else "Aucune fissure significative détectée."
        ),
        "trigger_level_2": crack,
    }


def predict_level_2(image: Image.Image) -> list[dict]:
    array = np.asarray(image.resize((300, 300)), dtype=np.float32)
    batch = np.expand_dims(preprocess_input(array), 0)
    started = perf_counter()
    probabilities = np.asarray(efficientnet().predict(batch, verbose=0)).reshape(-1)
    elapsed = perf_counter() - started
    if len(probabilities) != len(LABELS):
        raise ValueError("Nombre de sorties EfficientNetB3 inattendu.")

    results = []
    for label in LABELS:
        score = float(probabilities[LABELS.index(label)])
        if score >= THRESHOLDS[label]:
            class_name, priority, recommendation = MAPPING[label]
            results.append({
                "model_name": "EfficientNetB3", "original_label": label,
                "class_name": class_name, "confidence": score,
                "threshold": THRESHOLDS[label], "inference_time": elapsed,
                "priority": priority, "recommendation": recommendation,
            })
    if len(results) > 1:
        non_background = [
            item for item in results if item["original_label"] != "Background"
        ]
        if non_background:
            results = non_background
    if not results:
        best_label = max(LABELS, key=lambda x: float(probabilities[LABELS.index(x)]))
        score = float(probabilities[LABELS.index(best_label)])
        class_name, priority, recommendation = MAPPING[best_label]
        results.append({
            "model_name": "EfficientNetB3", "original_label": best_label,
            "class_name": class_name, "confidence": score,
            "threshold": THRESHOLDS[best_label], "inference_time": elapsed,
            "priority": priority,
            "recommendation": recommendation + " Classe la plus probable retenue sous les seuils optimisés.",
        })
    return sorted(results, key=lambda item: item["confidence"], reverse=True)


def run_pipeline(image: Image.Image) -> tuple[dict, list[dict]]:
    image = image.convert("RGB")
    level_1 = predict_level_1(image)
    return level_1, predict_level_2(image) if level_1["trigger_level_2"] else []
