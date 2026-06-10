"""
Run this script ONCE to train and save the model.
Usage: python train.py

Dataset: Download from Kaggle
Link: https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction
Place the CSV as: data/jobs.csv
"""

import pandas as pd
import os
from model import FakeJobDetector


def main():
    dataset_path = "data/jobs.csv"

    if not os.path.exists(dataset_path):
        print("❌ Dataset not found!")
        print("👉 Download from: https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction")
        print("👉 Save as: data/jobs.csv")
        return

    print("📂 Loading dataset...")
    df = pd.read_csv(dataset_path)
    print(f"   Total records: {len(df)}")
    print(f"   Fake jobs: {df['fraudulent'].sum()} ({df['fraudulent'].mean()*100:.1f}%)")
    print(f"   Real jobs: {(df['fraudulent'] == 0).sum()}")

    detector = FakeJobDetector()
    metrics = detector.train(df)
    detector.save()

    print("\n" + "="*50)
    print("📊 FINAL MODEL METRICS")
    print("="*50)
    print(f"Accuracy : {metrics['accuracy']}%")
    print(f"F1 Score : {metrics['f1_score']}%")
    print(f"ROC-AUC  : {metrics['roc_auc']}%")
    print("\nClassification Report:")
    print(metrics["classification_report"])
    print("✅ Training complete! Now run: streamlit run app.py")


if __name__ == "__main__":
    main()
