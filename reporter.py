import os
import csv
import pandas as pd
from datetime import datetime

REPORT_FILE = "reports/reported_jobs.csv"

COLUMNS = [
    "reported_at", "job_title", "company_name", "contact_email",
    "job_description", "risk_score", "verdict", "red_flags_count",
    "reported_by_reason"
]


def _ensure_file():
    """Create the reports CSV with headers if it doesn't exist."""
    os.makedirs("reports", exist_ok=True)
    if not os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()


def save_report(
    job_title: str,
    company_name: str,
    contact_email: str,
    job_description: str,
    risk_score: float,
    verdict: str,
    red_flags_count: int,
    reported_by_reason: str = "User reported"
) -> bool:
    """
    Save a suspicious job report to CSV.
    Returns True on success, False on failure.
    """
    try:
        _ensure_file()
        row = {
            "reported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "job_title": job_title,
            "company_name": company_name,
            "contact_email": contact_email,
            "job_description": job_description[:500],   # truncate long descriptions
            "risk_score": risk_score,
            "verdict": verdict,
            "red_flags_count": red_flags_count,
            "reported_by_reason": reported_by_reason,
        }
        with open(REPORT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False


def load_reports() -> pd.DataFrame:
    """Load all reported jobs as a DataFrame."""
    _ensure_file()
    df = pd.read_csv(REPORT_FILE)
    return df


def get_report_count() -> int:
    """Return total number of reports."""
    try:
        df = load_reports()
        return len(df)
    except:
        return 0


def delete_report(index: int) -> bool:
    """Delete a report by row index."""
    try:
        df = load_reports()
        df = df.drop(index=index).reset_index(drop=True)
        df.to_csv(REPORT_FILE, index=False)
        return True
    except:
        return False
