"""
Page Streamlit — Import du référentiel d'inspections.

À intégrer dans l'app existante. Si l'app utilise la structure multipage
Streamlit (dossier pages/), place ce fichier dans pages/ sous un nom du type
"6_Import_Referentiel.py" pour qu'il apparaisse dans le menu latéral.
Sinon, colle le contenu de la fonction render_import_page() comme un onglet
ou une section de app.py existant.

Réutilise le module import_referentiel.py déjà validé en ligne de commande —
aucune logique métier n'est dupliquée ici, seulement l'interface.
"""

import tempfile
from pathlib import Path

import streamlit as st

from import_referentiel import import_referentiel, REQUIRED_COLUMNS


def render_import_page():
    st.title("Import du référentiel d'inspections")

    st.markdown(
        """
        Importez un fichier **CSV, XLSX ou JSON** contenant un référentiel
        d'inspections à intégrer à la base. Colonnes obligatoires :
        """
    )
    st.code(", ".join(REQUIRED_COLUMNS), language=None)

    st.markdown(
        "Chaque ligne est validée avant insertion (drone existant, date, "
        "statut, type d'infrastructure). Les lignes invalides sont rejetées "
        "individuellement et documentées ci-dessous — l'import des lignes "
        "valides n'est jamais bloqué par les lignes en erreur."
    )

    uploaded_file = st.file_uploader(
        "Fichier à importer", type=["csv", "xlsx", "xls", "json"]
    )

    if uploaded_file is None:
        return

    # Sauvegarde temporaire nécessaire car import_referentiel() lit un chemin disque
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    if st.button("Lancer l'import", type="primary"):
        with st.spinner("Validation et insertion en cours..."):
            try:
                report = import_referentiel(tmp_path)
            except Exception as exc:
                st.error(f"Échec de l'import : {exc}")
                return

        col1, col2, col3 = st.columns(3)
        col1.metric("Lignes totales", report["total_rows"])
        col2.metric("Insérées", report["inserted"])
        col3.metric("Rejetées", report["rejected"])

        if report["inserted"] > 0:
            st.success(
                f"{report['inserted']} inspection(s) ajoutée(s) à la base."
            )

        if report["errors"]:
            st.warning(f"{len(report['errors'])} ligne(s) rejetée(s) — détail ci-dessous :")
            st.dataframe(
                [
                    {"Ligne": err["row"], "Raisons du rejet": "; ".join(err["reasons"])}
                    for err in report["errors"]
                ],
                use_container_width=True,
            )

        st.caption(
            f"Import horodaté le {report['imported_at']} — "
            f"rapport archivé : {report['report_path']}"
        )


if __name__ == "__main__":
    render_import_page()
