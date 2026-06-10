import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, accuracy_score, f1_score
)
from imblearn.over_sampling import SMOTE
from preprocess import prepare_features

MODEL_PATH = "models/rf_model.pkl"
VECTORIZER_PATH = "models/tfidf_vectorizer.pkl"


# ─────────────────────────────────────────────
# Model Wrapper Class
# ─────────────────────────────────────────────
class FakeJobDetector:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",   # handles class imbalance
            random_state=42,
            n_jobs=-1
        )
        self.vectorizer = None
        self.is_trained = False

    def train(self, df: pd.DataFrame):
        """Train the model on a labeled dataframe."""
        print("⚙️  Preparing features...")
        X, self.vectorizer = prepare_features(df, fit=True)
        y = df["fraudulent"].astype(int).values

        # Handle class imbalance with SMOTE
        print("⚖️  Balancing classes with SMOTE...")
        smote = SMOTE(random_state=42)
        X_res, y_res = smote.fit_resample(X, y)

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_res, y_res, test_size=0.2, random_state=42, stratify=y_res
        )

        print("🌲 Training Random Forest...")
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
            "f1_score": round(f1_score(y_test, y_pred) * 100, 2),
            "roc_auc": round(roc_auc_score(y_test, y_prob) * 100, 2),
            "classification_report": classification_report(y_test, y_pred),
            "confusion_matrix": confusion_matrix(y_test, y_pred),
        }

        print(f"✅ Accuracy: {metrics['accuracy']}%")
        print(f"✅ F1 Score: {metrics['f1_score']}%")
        print(f"✅ ROC-AUC:  {metrics['roc_auc']}%")
        return metrics

    def predict(self, df: pd.DataFrame):
        """Returns (label, probability) for each row."""
        X, _ = prepare_features(df, vectorizer=self.vectorizer, fit=False)
        labels = self.model.predict(X)
        probs = self.model.predict_proba(X)[:, 1]
        return labels, probs

    def predict_single(self, job_dict: dict):
        """Predict on a single job posting dict."""
        df = pd.DataFrame([job_dict])
        labels, probs = self.predict(df)
        return int(labels[0]), float(probs[0])

    def save(self):
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        joblib.dump(self.vectorizer, VECTORIZER_PATH)
        print(f"💾 Model saved to {MODEL_PATH}")

    def load(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Model not found. Please run train.py first.")
        self.model = joblib.load(MODEL_PATH)
        self.vectorizer = joblib.load(VECTORIZER_PATH)
        self.is_trained = True
        print("✅ Model loaded successfully.")
