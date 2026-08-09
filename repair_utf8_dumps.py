"""Répare les littéraux remplacés par '?' dans les dumps historiques.

Le fichier d'entrée et le fichier de sortie sont toujours lus/écrits en UTF-8.
Le script est idempotent : une seconde exécution ne modifie plus le résultat.
"""

from __future__ import annotations

import argparse
from pathlib import Path


REPLACEMENTS = {
    "Administrateur D?mo": "Administrateur Démo",
    "Inspecteur D?mo": "Inspecteur Démo",
    "B??timent": "Bâtiment",
    "Pyl??ne": "Pylône",
    "Planifi??e": "Planifiée",
    "Termin??e": "Terminée",
    "Annul??e": "Annulée",
    "d??monstration": "démonstration",
    "synth??tique": "synthétique",
    "g??n??r??e": "générée",
    "d??gag??": "dégagé",
    "l??g??re": "légère",
    "mod??r??": "modéré",
    "entrep??t": "entrepôt",
    "Contr??le": "Contrôle",
    "contr??le": "contrôle",
    "p??riodique": "périodique",
    "fa??ade": "façade",
    "b??ton": "béton",
    "d??faut": "défaut",
    "D??faut": "Défaut",
    "d??tect??e": "détectée",
    "d??tecter": "détecter",
    "Pr??sence": "Présence",
    "pr??sence": "présence",
    "??l??ments": "éléments",
    "m??talliques": "métalliques",
    "D??p??ts": "Dépôts",
    "d??p??ts": "dépôts",
    "blanch??tres": "blanchâtres",
    "min??raux": "minéraux",
    "??clatement": "Éclatement",
    "d??tachement": "détachement",
    "Armatures m??talliques": "Armatures métalliques",
    "n??cessaire": "nécessaire",
    "n??cessaires": "nécessaires",
    "S??curiser": "Sécuriser",
    "r??paration": "réparation",
    "d??t??rior??": "détérioré",
    "pr??sentant": "présentant",
    "compl??mentaire": "complémentaire",
    "d??taill??e": "détaillée",
    "l'origine de l'humidit??": "l'origine de l'humidité",
    "humidit??": "humidité",
    "l'??volution": "l'évolution",
    "??volution": "évolution",
    "Pr??voir": "Prévoir",
    "imm??diatement": "immédiatement",
    "imm??diate": "immédiate",
    "Une fissure a ??t??": "Une fissure a été",
    "Aucune fissure d??tect??e": "Aucune fissure détectée",
    "Aucun d??faut": "Aucun défaut",
    "R??parer": "Réparer",
    "Cr??ation": "Création",
    "Pr??diction": "Prédiction",
    "pr??diction": "prédiction",
    "Ajout mod??les": "Ajout modèles",
    "Mod??le": "Modèle",
    "mod??le": "modèle",
    "r??sultat": "résultat",
    "ins??r??e": "insérée",
    "import??e": "importée",
    "analys??e": "analysée",
    "lanc??e": "lancée",
    "lanc??": "lancé",
    "enregistr??e": "enregistrée",
    "enregistr??": "enregistré",
    "recommand??e": "recommandée",
    "significatif d??tect??": "significatif détecté",
    "?? deux niveaux": "à deux niveaux",
    "suite ??": "suite à",
    " ?? partir": " à partir",
    "captur??es": "capturées",
    "r??alis??e": "réalisée",
    "??le-de-France": "Île-de-France",
    "d???inspection": "d'inspection",
    "d???un": "d'un",
    "d???images": "d'images",
    "l?????tat": "l'état",
    "n??": "n°",
    "th??se": "thèse",
    "r??f??rentiel": "référentiel",
    "succ??s": "succès",
    " ?? ": " à ",
    "G??n°ration": "Génération",
    "Ex??cution": "Exécution",
    "pyl??ne": "pylône",
    "utilis??": "utilisé",
    "l???absence": "l'absence",
}


def repair_dump(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    for corrupted, corrected in REPLACEMENTS.items():
        text = text.replace(corrupted, corrected)
    path.write_text(text, encoding="utf-8", newline="\n")
    return sum(original.count(value) for value in REPLACEMENTS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.paths:
        replacements = repair_dump(path)
        print(f"{path}: {replacements} remplacement(s), sortie UTF-8")


if __name__ == "__main__":
    main()
