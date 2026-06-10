from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import json

app = Flask(__name__)

# ── Load model once at startup ──
from model import FakeJobDetector
detector = FakeJobDetector()
model_ready = False
try:
    detector.load()
    model_ready = True
    print("✅ Model loaded.")
except FileNotFoundError:
    print("⚠️  Model not found. Run train.py first.")


def get_dataset():
    path = "data/jobs.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


# ════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════

@app.route("/")
def home():
    from reporter import get_report_count
    df = get_dataset()
    stats = {
        "model_ready": model_ready,
        "report_count": get_report_count(),
        "dataset_count": len(df) if df is not None else 0,
    }
    return render_template("index.html", stats=stats)


@app.route("/analyze")
def analyze_page():
    return render_template("analyze.html", model_ready=model_ready)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    if not model_ready:
        return jsonify({"error": "Model not loaded. Run train.py first."}), 503

    data = request.get_json()
    raw_text = data.get("raw_text", "").strip()

    if not raw_text or len(raw_text) < 30:
        return jsonify({"error": "Please paste a job posting with enough content."}), 400

    # Extract fields
    from extractor import extract_all
    extracted = extract_all(raw_text)

    # Build job dict
    job_dict = {
        "title":               extracted["title"],
        "company_profile":     extracted["company_profile"],
        "description":         extracted["description"],
        "requirements":        extracted["requirements"],
        "benefits":            extracted["benefits"],
        "location":            extracted["location"],
        "salary_range":        extracted["salary_range"],
        "employment_type":     extracted["employment_type"],
        "required_experience": extracted["experience"],
        "has_company_logo":    0,
        "has_questions":       0,
        "contact_email":       extracted["contact_email"],
    }

    # ML prediction
    label, prob = detector.predict_single(job_dict)
    job_dict["_ml_prob"] = prob

    # Rule engine
    from explainer import explain_job
    analysis = explain_job(job_dict)

    # Email validation
    from validators import validate_email, validate_salary
    email_result = validate_email(extracted["contact_email"])
    salary_result = validate_salary(extracted["salary_range"], extracted["title"])

    return jsonify({
        "extracted": {
            "title":          extracted["title"],
            "company_name":   extracted["company_name"],
            "location":       extracted["location"],
            "salary_range":   extracted["salary_range"],
            "contact_email":  extracted["contact_email"],
            "contact_phone":  extracted["contact_phone"],
            "company_website":extracted["company_website"],
            "employment_type":extracted["employment_type"],
            "experience":     extracted["experience"],
        },
        "ml": {
            "label": int(label),
            "probability": round(float(prob) * 100, 1),
        },
        "analysis": {
            "risk_score":       analysis["risk_score"],
            "verdict":          analysis["verdict"],
            "verdict_color":    analysis["verdict_color"],
            "rule_flags_count": analysis["rule_flags_count"],
            "red_flags":        analysis["red_flags"],
        },
        "validation": {
            "email": {
                "is_valid":      email_result["is_valid"],
                "is_free_domain":email_result["is_free_domain"],
                "domain":        email_result["domain"],
                "flags":         email_result["flags"],
            },
            "salary": {
                "flags": salary_result["flags"],
                "suspicious": salary_result["suspicious"],
            }
        }
    })


@app.route("/api/report", methods=["POST"])
def api_report():
    data = request.get_json()
    from reporter import save_report
    ok = save_report(
        job_title=data.get("job_title", ""),
        company_name=data.get("company_name", ""),
        contact_email=data.get("contact_email", ""),
        job_description=data.get("job_description", ""),
        risk_score=data.get("risk_score", 0),
        verdict=data.get("verdict", ""),
        red_flags_count=data.get("red_flags_count", 0),
        reported_by_reason=data.get("reason", "User reported"),
    )
    return jsonify({"success": ok})


@app.route("/dashboard")
def dashboard():
    df = get_dataset()
    if df is None:
        return render_template("dashboard.html", error=True, charts={})

    # Prepare chart data as JSON for frontend
    from reporter import get_report_count

    # Class distribution
    counts = df["fraudulent"].value_counts().to_dict()
    real_count = int(counts.get(0, 0))
    fake_count = int(counts.get(1, 0))

    # Employment type
    if "employment_type" in df.columns:
        emp = df.groupby(["employment_type", "fraudulent"]).size().reset_index(name="count")
        emp_data = emp.to_dict(orient="records")
    else:
        emp_data = []

    # Description length
    df["desc_len"] = df.get("description", pd.Series([""] * len(df))).fillna("").str.len()
    real_lens = df[df["fraudulent"]==0]["desc_len"].tolist()[:500]
    fake_lens = df[df["fraudulent"]==1]["desc_len"].tolist()[:500]

    # Top industries
    if "industry" in df.columns:
        ind = df.groupby("industry")["fraudulent"].agg(["sum","count"]).reset_index()
        ind.columns = ["industry","fake","total"]
        ind = ind[ind["total"] > 20].copy()
        ind["pct"] = (ind["fake"] / ind["total"] * 100).round(1)
        ind = ind.sort_values("pct", ascending=False).head(10)
        ind_data = ind.to_dict(orient="records")
    else:
        ind_data = []

    charts = {
        "real": real_count,
        "fake": fake_count,
        "total": real_count + fake_count,
        "fake_pct": round(fake_count / (real_count + fake_count) * 100, 1),
        "emp_data": emp_data,
        "real_lens": real_lens,
        "fake_lens": fake_lens,
        "ind_data": ind_data,
        "report_count": get_report_count(),
    }

    return render_template("dashboard.html", error=False, charts=json.dumps(charts))


@app.route("/reports")
def reports_page():
    from reporter import load_reports, get_report_count
    df_rep = load_reports()
    reports = df_rep.to_dict(orient="records") if len(df_rep) > 0 else []
    return render_template("reports.html", reports=reports, count=get_report_count())


@app.route("/api/delete-report/<int:idx>", methods=["DELETE"])
def delete_report_api(idx):
    from reporter import delete_report
    ok = delete_report(idx)
    return jsonify({"success": ok})


@app.route("/api/download-reports")
def download_reports():
    path = "reports/reported_jobs.csv"
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return jsonify({"error": "No reports found"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
