import re
import string
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

# ─────────────────────────────────────────────
# Suspicious keyword patterns
# ─────────────────────────────────────────────
SUSPICIOUS_KEYWORDS = [
    "no experience needed", "work from home guaranteed", "earn from home",
    "make money fast", "unlimited income", "be your own boss", "financial freedom",
    "investment required", "send your bank details", "wire transfer",
    "western union", "money order", "processing fee", "registration fee",
    "guaranteed job", "no interview", "immediate joining", "urgent hiring",
    "weekly payment", "daily payment", "100% profit", "double your income",
    "part time earn", "data entry work from home", "reseller",
    "multi level marketing", "mlm", "network marketing", "pyramid",
    "whatsapp me", "telegram me", "contact directly", "no degree required",
    "no qualification", "anyone can apply", "housewife", "student job",
    "earn 50000", "earn 1 lakh", "5000 per day", "10000 per day",
]

SCAM_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "rediffmail.com", "ymail.com", "aol.com", "mail.com"
]


# ─────────────────────────────────────────────
# Text Cleaning
# ─────────────────────────────────────────────
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " url ", text)          # URLs
    text = re.sub(r"\S+@\S+", " email ", text)                # Emails
    text = re.sub(r"\d+", " num ", text)                      # Numbers
    text = re.sub(r"[^\w\s]", " ", text)                      # Punctuation
    text = re.sub(r"\s+", " ", text).strip()                  # Extra spaces
    return text


# ─────────────────────────────────────────────
# Feature Engineering
# ─────────────────────────────────────────────
def extract_meta_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract hand-crafted numeric features from raw dataframe columns."""
    features = pd.DataFrame()

    # Text-based features
    full_text = (
        df.get("title", pd.Series([""] * len(df))).fillna("") + " " +
        df.get("company_profile", pd.Series([""] * len(df))).fillna("") + " " +
        df.get("description", pd.Series([""] * len(df))).fillna("") + " " +
        df.get("requirements", pd.Series([""] * len(df))).fillna("") + " " +
        df.get("benefits", pd.Series([""] * len(df))).fillna("")
    ).str.lower()

    features["text_length"] = full_text.str.len()
    features["word_count"] = full_text.str.split().str.len()
    features["exclamation_count"] = full_text.str.count("!")
    features["question_count"] = full_text.str.count(r"\?")
    features["caps_ratio"] = full_text.apply(
        lambda x: sum(1 for c in x if c.isupper()) / max(len(x), 1)
    )

    # Suspicious keyword count
    features["suspicious_keyword_count"] = full_text.apply(
        lambda x: sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in x)
    )

    # Email domain flag
    email_col = df.get("required_experience", pd.Series([""] * len(df))).fillna("")
    features["has_free_email"] = df.get("location", pd.Series([""] * len(df))).fillna("").apply(
        lambda x: 0  # placeholder; real email check done in validators.py
    )

    # Has company logo
    features["has_logo"] = df.get("has_company_logo", pd.Series([0] * len(df))).fillna(0).astype(int)

    # Has questions
    features["has_questions"] = df.get("has_questions", pd.Series([0] * len(df))).fillna(0).astype(int)

    # Employment type encoding
    emp_map = {
        "Full-time": 0, "Part-time": 1, "Contract": 2,
        "Temporary": 3, "Other": 4, "": 5
    }
    features["employment_type"] = df.get(
        "employment_type", pd.Series([""] * len(df))
    ).fillna("").map(emp_map).fillna(5).astype(int)

    # Required experience encoding
    exp_map = {
        "Not Applicable": 0, "Internship": 1, "Entry level": 2,
        "Associate": 3, "Mid-Senior level": 4, "Director": 5,
        "Executive": 6, "": 7
    }
    features["required_experience"] = df.get(
        "required_experience", pd.Series([""] * len(df))
    ).fillna("").map(exp_map).fillna(7).astype(int)

    # Missing fields count (a strong signal for fake jobs)
    important_cols = ["company_profile", "description", "requirements", "benefits", "salary_range"]
    features["missing_fields"] = sum(
        df.get(col, pd.Series([None] * len(df))).isna().astype(int)
        for col in important_cols
    )

    return features


def build_combined_text(df: pd.DataFrame) -> pd.Series:
    """Combine all text columns into one for TF-IDF."""
    cols = ["title", "company_profile", "description", "requirements", "benefits"]
    combined = pd.Series([""] * len(df))
    for col in cols:
        if col in df.columns:
            combined = combined + " " + df[col].fillna("").apply(clean_text)
    return combined.str.strip()


def prepare_features(df: pd.DataFrame, vectorizer=None, fit=False):
    """
    Full feature pipeline:
    Returns (X, vectorizer) where X is a numpy array ready for the model.
    """
    # TF-IDF on combined text
    combined_text = build_combined_text(df)

    if fit:
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=2
        )
        tfidf_matrix = vectorizer.fit_transform(combined_text).toarray()
    else:
        tfidf_matrix = vectorizer.transform(combined_text).toarray()

    # Meta features
    meta = extract_meta_features(df).values

    # Stack TF-IDF + meta features
    X = np.hstack([tfidf_matrix, meta])
    return X, vectorizer
