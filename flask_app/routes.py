"""Routes HTML et API de DroneInspect Flask."""

from __future__ import annotations

import io
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import Blueprint, abort, jsonify, render_template, request, send_file
from PIL import Image, UnidentifiedImageError

from flask_app.database import (
    admin_data, create_inspection, create_user, dashboard_data, datasets_list, drones,
    drones_list, import_inspections, inspection_history, inspections,
    prediction_history, reports_list, save_analysis, update_user,
)
from flask_app.pipeline import run_pipeline


web = Blueprint("web", __name__)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
IMPORT_EXTENSIONS = {".csv", ".xlsx", ".json"}

SECTIONS = {
    "accueil": ("Accueil", "🏠", "Vue générale de DroneInspect AI et accès aux principaux modules."),
    "datasets": ("Datasets", "📁", "Référentiels de données utilisés pour l’entraînement et l’évaluation."),
    "drones": ("Drones", "🚁", "Gestion du matériel et des drones affectés aux missions."),
    "inspections": ("Inspections", "📋", "Création et suivi des missions d’inspection."),
    "historique": ("Historique", "📊", "Consultation chronologique des analyses et des prédictions."),
    "rapports": ("Rapports", "📄", "Rapports métier et priorités d’intervention."),
    "dashboard": ("Dashboard", "📈", "Indicateurs opérationnels et synthèse de l’activité."),
    "telechargements": ("Téléchargements", "📥", "Exports CSV, XLSX, PDF et archives disponibles."),
    "administration": ("Administration", "⚙️", "Gestion des utilisateurs, modèles et journaux techniques."),
}


def _image_from_request():
    uploaded = request.files.get("image")
    if uploaded is None or not uploaded.filename:
        raise ValueError("Une image est obligatoire.")
    if Path(uploaded.filename).suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError("Formats image acceptés : JPG, PNG et WEBP.")
    try:
        image = Image.open(uploaded.stream)
        image.load()
        return image.convert("RGB"), uploaded.filename
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Le fichier transmis n'est pas une image valide.") from exc


def _inspection_id() -> int:
    raw = request.form.get("inspection_id", "")
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError("inspection_id doit être un entier.") from exc


def _serialize(level_1: dict, level_2: list[dict], saved: dict) -> dict:
    final = level_2 if level_2 else [level_1]
    return {
        "class_predicted": final[0].get("original_label", final[0]["class_name"]),
        "confidence": round(float(final[0]["confidence"]), 6),
        "confidence_percent": round(float(final[0]["confidence"]) * 100, 2),
        "level_1": level_1,
        "level_2": level_2,
        "database": saved,
    }


@web.get("/")
def index():
    return render_template("index.html", inspections=inspections(), result=None, error=None)


@web.get("/section/<section>")
def section_page(section: str):
    if section not in SECTIONS:
        return render_template(
            "section.html",
            section={"title": "Page introuvable", "icon": "⚠️", "description": "Ce module n’existe pas."},
            active_page="",
        ), 404
    title, icon, description = SECTIONS[section]
    if section == "accueil":
        return render_template(
            "home.html", active_page=section, data=dashboard_data(),
            recent=prediction_history(8),
        )
    if section == "dashboard":
        return render_template(
            "dashboard.html", active_page=section, data=dashboard_data(),
        )
    if section == "datasets":
        return render_template(
            "table_page.html", active_page=section, title=title, icon=icon,
            description=description, rows=datasets_list(),
            columns=[("dataset_id", "ID"), ("dataset_name", "Dataset"),
                     ("description", "Description"), ("total_images", "Images"),
                     ("source", "Source")],
        )
    if section == "drones":
        return render_template(
            "table_page.html", active_page=section, title=title, icon=icon,
            description=description, rows=drones_list(),
            columns=[("drone_id", "ID"), ("drone_name", "Drone"),
                     ("drone_model", "Modèle"), ("camera_resolution", "Caméra"),
                     ("max_flight_time", "Autonomie"), ("description", "Description")],
        )
    if section == "historique":
        return render_template(
            "table_page.html", active_page=section, title=title, icon=icon,
            description=description, rows=prediction_history(),
            columns=[("prediction_date", "Date"), ("inspection_id", "Inspection"),
                     ("location", "Lieu"), ("model_name", "Modèle"),
                     ("class_name", "Classe"), ("confidence", "Confiance (%)"),
                     ("intervention_priority", "Priorité")], export_name="historique",
        )
    if section == "rapports":
        rows = reports_list()
        selected_id = request.args.get("report_id", type=int)
        selected = next(
            (row for row in rows if row["report_id"] == selected_id),
            rows[0] if rows else None,
        )
        return render_template(
            "reports.html", active_page=section, rows=rows, selected=selected,
        )
    if section == "telechargements":
        return render_template(
            "downloads.html", active_page=section,
            inspections_rows=inspection_history(),
            predictions_rows=prediction_history(),
            reports_rows=reports_list(),
            logs_count=len(admin_data()["logs"]),
        )
    if section == "administration":
        return render_template("administration.html", active_page=section, data=admin_data())
    return render_template(
        "section.html",
        section={"title": title, "icon": icon, "description": description},
        active_page=section,
    )


def _report_or_404(report_id: int) -> dict:
    report = next(
        (row for row in reports_list(None) if row["report_id"] == report_id), None
    )
    if report is None:
        abort(404)
    return report


@web.get("/rapports/<int:report_id>/image")
def report_image(report_id: int):
    report = _report_or_404(report_id)
    image_path = (Path(__file__).resolve().parents[1] / str(report.get("image_path") or "")).resolve()
    project_root = Path(__file__).resolve().parents[1]
    if not image_path.is_relative_to(project_root) or not image_path.is_file():
        abort(404)
    return send_file(image_path, download_name=report.get("image_name") or image_path.name)


@web.get("/rapports/<int:report_id>/pdf")
def report_pdf(report_id: int):
    report = _report_or_404(report_id)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        lines = [
            f"DroneInspect AI - Rapport {report_id}",
            f"Inspection : {report.get('inspection_id', '-')}",
            f"Date : {report.get('inspection_date') or '-'}",
            f"Lieu : {report.get('location') or '-'}",
            f"Infrastructure : {report.get('infrastructure_type') or '-'}",
            f"Modele IA : {report.get('model_name') or '-'}",
            f"Defaut : {report.get('class_name') or '-'}",
            f"Confiance : {float(report.get('confidence') or 0):.2f} %",
            f"Priorite : {report.get('intervention_priority') or '-'}",
            f"Recommandation : {report.get('recommendation') or '-'}",
        ]
        content = ["BT", "/F1 12 Tf", "50 790 Td"]
        for index, line in enumerate(lines):
            safe = (str(line).encode("latin-1", "replace").decode("latin-1")
                    .replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)"))
            if index:
                content.append("0 -24 Td")
            content.append(f"({safe}) Tj")
        content.append("ET")
        stream = "\n".join(content).encode("latin-1")
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        ]
        pdf_data = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for number, obj in enumerate(objects, 1):
            offsets.append(len(pdf_data))
            pdf_data.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
        xref = len(pdf_data)
        pdf_data.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
        for offset in offsets[1:]:
            pdf_data.extend(f"{offset:010d} 00000 n \n".encode())
        pdf_data.extend(
            f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
        )
        return send_file(io.BytesIO(pdf_data), mimetype="application/pdf", as_attachment=True,
                         download_name=f"rapport_inspection_{report_id}.pdf")

    output = io.BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    width, height = A4
    pdf.setTitle(f"Rapport DroneInspect {report_id}")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, height - 60, f"DroneInspect AI - Rapport n°{report_id}")
    fields = [
        ("Inspection", f"n°{report.get('inspection_id', '—')}"),
        ("Date", str(report.get("inspection_date") or "—")),
        ("Lieu", str(report.get("location") or "—")),
        ("Infrastructure", str(report.get("infrastructure_type") or "—")),
        ("Inspecteur", str(report.get("inspector_name") or "—")),
        ("Drone", str(report.get("drone") or "—")),
        ("Modèle IA", str(report.get("model_name") or "—")),
        ("Défaut", str(report.get("class_name") or "—")),
        ("Confiance", f"{float(report.get('confidence') or 0):.2f} %"),
        ("Priorité", str(report.get("intervention_priority") or "—")),
    ]
    y = height - 105
    for label, value in fields:
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(50, y, f"{label} :")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(155, y, value[:90])
        y -= 25
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Recommandation :")
    pdf.setFont("Helvetica", 10)
    recommendation = str(report.get("recommendation") or "—")
    for start in range(0, len(recommendation), 90):
        y -= 18
        pdf.drawString(50, y, recommendation[start:start + 90])
    pdf.save()
    output.seek(0)
    return send_file(output, mimetype="application/pdf", as_attachment=True,
                     download_name=f"rapport_inspection_{report_id}.pdf")


@web.get("/exports/<name>.<extension>")
def export_data(name: str, extension: str):
    sources = {
        "inspections": inspection_history,
        "historique": lambda: prediction_history(None),
        "rapports": lambda: reports_list(None),
        "datasets": datasets_list,
        "drones": drones_list,
    }
    if name not in sources or extension not in {"csv", "xlsx"}:
        return jsonify({"error": "Export inconnu."}), 404
    frame = pd.DataFrame(sources[name]())
    output = io.BytesIO()
    if extension == "csv":
        output.write(frame.to_csv(index=False).encode("utf-8-sig"))
        mimetype = "text/csv"
    else:
        frame.to_excel(output, index=False, engine="openpyxl")
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    output.seek(0)
    return send_file(output, mimetype=mimetype, as_attachment=True,
                     download_name=f"droneinspect_{name}.{extension}")


@web.get("/exports/complet.zip")
def export_complete_zip():
    sources = {
        "inspections": inspection_history(), "predictions": prediction_history(None),
        "rapports": reports_list(None), "datasets": datasets_list(),
        "drones": drones_list(), "utilisateurs": admin_data()["users"],
        "modeles": admin_data()["models"], "logs": admin_data()["logs"],
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, rows in sources.items():
            archive.writestr(
                f"{name}.csv", pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
            )
    output.seek(0)
    return send_file(
        output, mimetype="application/zip", as_attachment=True,
        download_name=f"droneinspect_export_complet_{datetime.now():%Y%m%d_%H%M%S}.zip",
    )


@web.route("/section/administration", methods=["GET", "POST"])
def administration_page():
    message = error = None
    active_tab = request.form.get("active_tab", request.args.get("tab", "users"))
    if request.method == "POST":
        try:
            action = request.form.get("action")
            if action == "create":
                user_id = create_user(
                    request.form.get("full_name", ""), request.form.get("email", ""),
                    request.form.get("role", "Inspecteur"),
                )
                message = f"Utilisateur n°{user_id} créé avec succès."
            elif action == "update":
                update_user(
                    int(request.form.get("user_id", 0)),
                    request.form.get("role", "Inspecteur"),
                    request.form.get("is_active") == "on",
                )
                message = "Utilisateur modifié avec succès."
            else:
                raise ValueError("Action inconnue.")
        except Exception as exc:
            error = str(exc)
    return render_template(
        "administration.html", active_page="administration", data=admin_data(),
        message=message, error=error, active_tab=active_tab,
    )


@web.route("/section/inspections", methods=["GET", "POST"])
def inspections_page():
    message = error = None
    active_tab = request.args.get("tab", "create")
    if request.method == "POST":
        try:
            inspection_id = create_inspection(request.form.to_dict())
            message = f"Inspection n°{inspection_id} enregistrée avec succès."
            active_tab = "history"
        except Exception as exc:
            error = str(exc)
            active_tab = "create"
    return render_template(
        "inspections.html",
        active_page="inspections",
        drones=drones(),
        rows=inspection_history(),
        message=message,
        error=error,
        active_tab=active_tab,
    )


@web.post("/analyze")
def analyze():
    try:
        inspection_id = _inspection_id()
        image, filename = _image_from_request()
        level_1, level_2 = run_pipeline(image)
        saved = save_analysis(inspection_id, image, filename, level_1, level_2)
        result = _serialize(level_1, level_2, saved)
        return render_template(
            "index.html", inspections=inspections(), result=result, error=None
        )
    except Exception as exc:
        return render_template(
            "index.html", inspections=inspections(), result=None, error=str(exc)
        ), 400


@web.post("/predict")
def predict_api():
    """API multipart : champs ``inspection_id`` et ``image``."""
    try:
        inspection_id = _inspection_id()
        image, filename = _image_from_request()
        level_1, level_2 = run_pipeline(image)
        saved = save_analysis(inspection_id, image, filename, level_1, level_2)
        return jsonify(_serialize(level_1, level_2, saved))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": "Échec de l'analyse.", "detail": str(exc)}), 500


def _read_import(uploaded) -> list[dict]:
    extension = Path(uploaded.filename).suffix.lower()
    if extension not in IMPORT_EXTENSIONS:
        raise ValueError("Formats d'import acceptés : CSV, XLSX et JSON.")
    content = uploaded.read()
    if extension == ".csv":
        frame = pd.read_csv(io.BytesIO(content))
    elif extension == ".xlsx":
        frame = pd.read_excel(io.BytesIO(content))
    else:
        frame = pd.read_json(io.BytesIO(content))
    frame = frame.where(pd.notna(frame), None)
    return frame.to_dict(orient="records")


@web.route("/imports", methods=["GET", "POST"])
def imports_page():
    message = error = None
    if request.method == "POST":
        try:
            uploaded = request.files.get("referential")
            if uploaded is None or not uploaded.filename:
                raise ValueError("Sélectionnez un fichier à importer.")
            rows = _read_import(uploaded)
            count = import_inspections(rows, uploaded.filename)
            message = f"Import réussi : {count} inspection(s) ajoutée(s) et journalisée(s)."
        except Exception as exc:
            error = str(exc)
    return render_template("imports.html", message=message, error=error)


@web.get("/health")
def health():
    return jsonify({"status": "ok", "service": "DroneInspect Flask"})


@web.app_errorhandler(413)
def too_large(_error):
    return jsonify({"error": "Fichier trop volumineux."}), 413
