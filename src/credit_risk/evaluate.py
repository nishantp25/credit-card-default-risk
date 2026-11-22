from pathlib import Path

import pandas as pd
from sklearn.metrics import auc, make_scorer, precision_recall_curve
from sklearn.model_selection import StratifiedKFold, cross_validate
from .modeling import build_forest_pipeline, build_logistic_pipeline
from .modeling import (
    build_boosting_pipeline,
    build_forest_pipeline,
    build_logistic_pipeline,
)

from .data import load_clients, split_clients
from .features import build_features
from .modeling import build_logistic_pipeline


def pr_auc(y_true, scores):
    precision, recall, _ = precision_recall_curve(y_true, scores)
    return auc(recall, precision)

def evaluate_model(model, X, y):
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = {
        "roc_auc": "roc_auc",
        "pr_auc": make_scorer(pr_auc, response_method="predict_proba"),
        "average_precision": "average_precision",
    }

    results = cross_validate(model, X, y, cv=folds, scoring=scoring, error_score="raise")
    return pd.DataFrame({name: results[f"test_{name}"] for name in scoring})

if __name__ == "__main__":
    clients = load_clients(Path("data/raw/default of credit card clients.xls"))
    train, _, _ = split_clients(clients)

    X = build_features(train)
    y = train["default payment next month"]

    models = {
        "Logistic regression": build_logistic_pipeline(),
        "Random forest": build_forest_pipeline(),
        "Gradient boosting": build_boosting_pipeline(),
    }

    for name, model in models.items():
        scores = evaluate_model(model, X, y)
        scores.index = range(1, len(scores) + 1)

        print(f"\n{name}")
        print(scores.rename_axis("fold").round(4))
        print(scores.agg(["mean", "std"]).round(4))