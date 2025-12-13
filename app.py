from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import csv
import os
import uuid
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from csv_reports_to_rdf import convert

# Use environment variable for Fuseki URL; default to localhost for local dev
FUSEKI_BASE = os.getenv("FUSEKI_BASE", "http://localhost:3030")
FUSEKI_ADMIN_USER = os.getenv("FUSEKI_ADMIN_USER", "admin")
FUSEKI_ADMIN_PASSWORD = os.getenv("FUSEKI_ADMIN_PASSWORD", "admin123")

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # change for production

CSV_FILE = "reports.csv"

# -------------------------------------------------------
# Create CSV with headers if it does not exist
# -------------------------------------------------------
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "case_id", "org_id", "input_by", "date_received", "date_recorded",
            "country", "state", "town", "village", "camp", "incident_date",
            "violence_type", "short_desc", "num_victims",
            "victim_age", "victim_gender",
            "num_perpetrators", "perp_affiliation",
            "pub_type", "pub_date", "pub_link"
        ])


# -------------------------------------------------------
# Helper
# -------------------------------------------------------
def current_role():
    return session.get("role")


def ensure_fuseki_dataset(dataset_name: str) -> None:
    """Ensure a Fuseki dataset exists; create it via admin API if missing."""
    datasets_url = f"{FUSEKI_BASE}/$/datasets"
    auth = HTTPBasicAuth(FUSEKI_ADMIN_USER, FUSEKI_ADMIN_PASSWORD)

    # Check existing datasets
    resp = requests.get(datasets_url, auth=auth, timeout=10)
    resp.raise_for_status()

    if dataset_name in resp.text:
        return

    # Create dataset as TDB2 store
    create_url = f"{FUSEKI_BASE}/$/datasets"
    params = {"dbName": dataset_name, "dbType": "tdb2"}
    resp = requests.post(create_url, params=params, auth=auth, timeout=10)
    resp.raise_for_status()


# -------------------------------------------------------
# LOGIN
# -------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        password = request.form.get("password")

        # Simple hardcoded demo passwords
        if role == "reporter" and password == "report123":
            session["role"] = "reporter"
            return redirect(url_for("report_form"))

        if role == "reviewer" and password == "review123":
            session["role"] = "reviewer"
            return redirect(url_for("reviewer_page"))

        return redirect(url_for("login", error=1))

    return render_template("login.html", role=current_role())


# -------------------------------------------------------
# REPORTER: FORM
# -------------------------------------------------------
@app.route("/report")
def report_form():
    # Protect route
    if current_role() != "reporter":
        return redirect(url_for("login", error=1))

    success = request.args.get("success")
    case_id = request.args.get("case_id")
    return render_template("form.html", role=current_role(),
                           success=success, case_id=case_id)


# -------------------------------------------------------
# REPORTER: SUBMIT HANDLER
# -------------------------------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    if current_role() != "reporter":
        return redirect(url_for("login", error=1))

    case_id = "CASE-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6]

    def safe(field):
        return request.form.get(field, "").strip()

    row = [
        case_id,
        safe("org_id"),
        safe("input_by"),
        safe("date_received"),
        safe("date_recorded"),
        safe("country"),
        safe("state"),
        safe("town"),
        safe("village"),
        safe("camp"),
        safe("incident_date"),
        safe("violence_type"),
        safe("short_desc"),
        safe("num_victims"),
        safe("victim_age"),
        safe("victim_gender"),
        safe("num_perpetrators"),
        safe("perp_affiliation"),
        safe("pub_type"),
        safe("pub_date"),
        safe("pub_link")
    ]

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    # Redirect back with success flag & case id for popup
    return redirect(url_for("report_form", success=1, case_id=case_id))


# -------------------------------------------------------
# REVIEWER DASHBOARD
# -------------------------------------------------------
@app.route("/reviewer")
def reviewer_page():
    if current_role() != "reviewer":
        return redirect(url_for("login", error=1))

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        data = list(reader)

    headers = data[0] if data else []
    rows = data[1:] if len(data) > 1 else []

    # Simple summary stats
    total_cases = len(rows)
    total_victims = 0
    for r in rows:
        try:
            total_victims += int(r[13])  # num_victims index
        except (ValueError, IndexError):
            continue

    return render_template(
        "reviewer.html",
        role=current_role(),
        headers=headers,
        rows=rows,
        total_cases=total_cases,
        total_victims=total_victims
    )


# -------------------------------------------------------
# LOGOUT
# -------------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------------------------------------------
# CONVERT CSV TO RDF AND UPLOAD TO FUSEKI
# -------------------------------------------------------
@app.route("/convert_and_upload", methods=["POST"])
def convert_and_upload():
    """Convert reports.csv to RDF and upload to Fuseki.

    Allowed for both reporter and reviewer roles.
    """

    if current_role() not in ("reporter", "reviewer"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    csv_path = CSV_FILE
    ttl_path = "reports_sord.ttl"

    if not os.path.exists(csv_path):
        return jsonify({"success": False, "message": "reports.csv not found"}), 404

    try:
        # 1) Convert CSV to RDF Turtle
        convert(csv_path, ttl_path)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Conversion failed: {e}"
        }), 500

    # Ensure dataset 'sord' exists before upload
    try:
        ensure_fuseki_dataset("sord")
    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "message": f"Could not ensure Fuseki dataset 'sord': {e}"
        }), 502

    # 2) Upload TTL directly to Fuseki dataset 'sord' using Graph Store Protocol
    data_url = f"{FUSEKI_BASE}/sord/data"

    try:
        with open(ttl_path, "r", encoding="utf-8") as f:
            ttl_data = f.read()

        headers = {"Content-Type": "text/turtle"}
        auth = HTTPBasicAuth(FUSEKI_ADMIN_USER, FUSEKI_ADMIN_PASSWORD)

        resp = requests.put(data_url, data=ttl_data, headers=headers, auth=auth, timeout=20)

        if resp.status_code not in (200, 201, 204):
            return jsonify({
                "success": False,
                "message": f"Fuseki upload failed (HTTP {resp.status_code}): {resp.text[:200]}"
            }), 502

    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "message": f"Could not reach Fuseki at {data_url}: {e}"
        }), 502

    return jsonify({
        "success": True,
        "message": "CSV converted to RDF and uploaded to Fuseki."
    })


# -------------------------------------------------------
# RUN
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
