from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import csv
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from schema import SCHEMA, validate_and_transform

# Load environment variables from .env
load_dotenv()

FUSEKI_BASE = os.getenv("FUSEKI_BASE", "http://localhost:3030")
FUSEKI_ADMIN_USER = os.getenv("FUSEKI_ADMIN_USER")
FUSEKI_ADMIN_PASSWORD = os.getenv("FUSEKI_ADMIN_PASSWORD")

AG_BASE_URL = os.getenv("AG_BASE_URL")
AG_REPO = os.getenv("AG_REPO")
AG_USER = os.getenv("AG_USER")
AG_PASSWORD = os.getenv("AG_PASSWORD")

REPORTER_PASS = os.getenv("REPORTER_PASSWORD")
REVIEWER_PASS = os.getenv("REVIEWER_PASSWORD")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

CSV_FILE = "reports.csv"
CSV_HEADERS = list(SCHEMA.keys())

# Create CSV with schema-driven headers if it does not exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        password = request.form.get("password")

        if role == "reporter" and password == REPORTER_PASS:
            session["role"] = role
            return redirect(url_for("form"))
        elif role == "reviewer" and password == REVIEWER_PASS:
            session["role"] = role
            return redirect(url_for("reviewer"))
        else:
            return render_template("login.html", error=True)

    return render_template("login.html")

@app.route("/form")
def form():
    if "role" not in session or session["role"] != "reporter":
        return redirect(url_for("login"))
    return render_template("form.html", role=session["role"])

@app.route("/reviewer")
def reviewer():
    if "role" not in session or session["role"] != "reviewer":
        return redirect(url_for("login"))

    rows = []
    display_headers = CSV_HEADERS  # Fallback

    if os.path.exists(CSV_FILE):
        # utf-8-sig safely ignores any invisible BOM characters
        with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            try:
                # 1. Grab the physical headers from the file
                file_headers = next(reader)
                if file_headers:
                    display_headers = file_headers
                
                # 2. Map data specifically to physical headers
                for row_data in reader:
                    # Skip completely blank lines
                    if any(str(cell).strip() for cell in row_data):
                        # Pad the row data safely in case the row is shorter than headers
                        padded_data = row_data + [""] * (len(display_headers) - len(row_data))
                        row_dict = dict(zip(display_headers, padded_data))
                        rows.append(row_dict)
            except StopIteration:
                pass

    # Pass the physical headers extracted directly from the file
    return render_template("reviewer.html", role=session["role"], headers=display_headers, rows=rows)

@app.route("/submit", methods=["POST"])
def submit():
    if "role" not in session or session["role"] != "reporter":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    # Schema-driven validation and transformation
    validated, errors = validate_and_transform(request.form)

    if errors:
        return jsonify({"success": False, "message": "Validation failed", "errors": errors}), 400

    # Guarantee column order mapped by SCHEMA keys
    row = [validated.get(field, "") for field in CSV_HEADERS]

    # Check if the file is missing or completely empty
    file_has_content = os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # If the file was deleted or is empty, write the headers first
        if not file_has_content:
            writer.writerow(CSV_HEADERS)
        writer.writerow(row)

    return jsonify({"success": True, "message": "Report submitted successfully."})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def ensure_fuseki_dataset(dataset_name):
    url = f"{FUSEKI_BASE}/$/datasets"
    auth = HTTPBasicAuth(FUSEKI_ADMIN_USER, FUSEKI_ADMIN_PASSWORD)
    resp = requests.get(url, auth=auth, timeout=10)
    if resp.status_code == 200:
        datasets = resp.json().get("datasets", [])
        for ds in datasets:
            if ds.get("ds.name") == f"/{dataset_name}":
                return True
    
    create_url = f"{FUSEKI_BASE}/$/datasets"
    data = {"dbName": dataset_name, "dbType": "tdb2"}
    requests.post(create_url, data=data, auth=auth, timeout=10)
    return True

@app.route("/convert_and_upload", methods=["POST"])
def convert_and_upload():
    if "role" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    ttl_path = "output.ttl"
    try:
        from csv_reports_to_rdf import convert
        convert(CSV_FILE, ttl_path)
    except Exception as e:
        return jsonify({"success": False, "message": f"Conversion failed: {e}"}), 500

    try:
        ensure_fuseki_dataset("sord")
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Could not ensure Fuseki dataset: {e}"}), 502

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

    return jsonify({"success": True, "message": "Data converted and uploaded to Fuseki successfully."})

@app.route("/convert_and_upload_allegrograph", methods=["POST"])
def convert_and_upload_allegrograph():
    if "role" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    ttl_path = "output.ttl"
    try:
        from csv_reports_to_rdf import convert
        convert(CSV_FILE, ttl_path)
    except Exception as e:
        return jsonify({"success": False, "message": f"Conversion failed: {e}"}), 500

    if not all([AG_BASE_URL, AG_REPO, AG_USER, AG_PASSWORD]):
        return jsonify({"success": False, "message": "AllegroGraph credentials not fully configured in environment."}), 500

    # Clean up the base URL in case '/webview' was accidentally included in the .env
    base_url = AG_BASE_URL.replace("/webview", "").rstrip("/")
    data_url = f"{base_url}/repositories/{AG_REPO}/statements"

    try:
        with open(ttl_path, "r", encoding="utf-8") as f:
            ttl_data = f.read()

        headers = {"Content-Type": "text/turtle"}
        auth = HTTPBasicAuth(AG_USER, AG_PASSWORD)
        
        # Allegrograph uses POST to /statements for inserting new data
        resp = requests.post(data_url, data=ttl_data, headers=headers, auth=auth, timeout=20)

        if resp.status_code not in (200, 201, 204):
            return jsonify({
                "success": False,
                "message": f"AllegroGraph upload failed (HTTP {resp.status_code}): {resp.text[:200]}"
            }), 502

    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "message": f"Could not reach AllegroGraph at {data_url}: {e}"
        }), 502

    return jsonify({"success": True, "message": "Data converted and uploaded to AllegroGraph successfully."})

if __name__ == "__main__":
    app.run(debug=False)