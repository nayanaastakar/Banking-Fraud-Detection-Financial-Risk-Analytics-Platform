from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from finguard.data_validation import detect_duplicates, report_nulls
from finguard.feature_engineering import add_derived_features


def fraud_overview(df: pd.DataFrame) -> dict:
    if "Class" not in df.columns:
        return {"fraudulent_transactions": 0, "legitimate_transactions": 0, "fraud_rate": 0.0}
    total = len(df)
    fraud = int(df["Class"].sum())
    legit = total - fraud
    return {
        "total_transactions": total,
        "fraudulent_transactions": fraud,
        "legitimate_transactions": legit,
        "fraud_rate": float(fraud / total) if total else 0.0,
    }


def generate_eda_plots(df: pd.DataFrame, output_dir: str | Path) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = add_derived_features(df.copy())
    plots = {}

    fig, ax = plt.subplots(figsize=(7, 5))
    counts = frame["Class"].value_counts().sort_index()
    labels = ["Legitimate", "Fraudulent"]
    ax.bar(labels, [counts.get(0, 0), counts.get(1, 0)], color=["steelblue", "tomato"])
    ax.set_title("Fraud vs Legitimate Transaction Count")
    ax.set_xlabel("Class")
    ax.set_ylabel("Transactions")
    fig.tight_layout()
    path = output_dir / "class_distribution.png"
    fig.savefig(path)
    plt.close(fig)
    plots["class_distribution"] = str(path)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(frame["Amount"], bins=40, kde=True, ax=ax)
    ax.set_title("Transaction Amount Distribution")
    ax.set_xlabel("Amount")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    path = output_dir / "amount_distribution.png"
    fig.savefig(path)
    plt.close(fig)
    plots["amount_distribution"] = str(path)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=frame, x="Class", y="Amount", ax=ax)
    ax.set_title("Amount Comparison by Transaction Class")
    ax.set_xlabel("Class")
    ax.set_ylabel("Amount")
    fig.tight_layout()
    path = output_dir / "amount_by_class.png"
    fig.savefig(path)
    plt.close(fig)
    plots["amount_by_class"] = str(path)

    if "Time" in frame.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(frame[frame["Class"] == 0]["Time"], label="Legitimate", bins=40, ax=ax, alpha=0.6)
        sns.histplot(frame[frame["Class"] == 1]["Time"], label="Fraudulent", bins=25, ax=ax, alpha=0.6)
        ax.set_title("Transaction Time Distribution by Class")
        ax.set_xlabel("Time (seconds from dataset start)")
        ax.set_ylabel("Frequency")
        ax.legend()
        fig.tight_layout()
        path = output_dir / "time_distribution.png"
        fig.savefig(path)
        plt.close(fig)
        plots["time_distribution"] = str(path)

    if any(col.startswith("V") for col in frame.columns):
        var_cols = [col for col in frame.columns if col.startswith("V")][:10]
        corr = frame[var_cols].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, cmap="coolwarm", center=0, annot=False, ax=ax)
        ax.set_title("Selected Feature Correlation Heatmap")
        fig.tight_layout()
        path = output_dir / "feature_correlation_heatmap.png"
        fig.savefig(path)
        plt.close(fig)
        plots["feature_correlation_heatmap"] = str(path)

    return plots
