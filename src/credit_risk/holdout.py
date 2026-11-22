from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix

from .artifacts import load_bundle
from .data import load_clients, split_clients
from .features import build_features
from .thresholds import MISSED_DEFAULT_COST


if __name__ == "__main__":
    clients = load_clients(Path("data/raw/default of credit card clients.xls"))
    _, _, test = split_clients(clients)
    bundle = load_bundle()

    scores = bundle["model"].predict_proba(build_features(test))[:, 1]
    predictions = pd.DataFrame({
        "ID": test["ID"],
        "actual_default": test["default payment next month"],
        "risk_score": scores,
        "flagged": scores >= bundle["cutoff"],
    })
    predictions.to_csv("artifacts/test_predictions.csv", index=False)

    tn, fp, fn, tp = confusion_matrix(
        predictions["actual_default"], predictions["flagged"], labels=[0, 1]
    ).ravel()

    print("Test customers:", len(predictions))
    print("Cutoff:", bundle["cutoff"])
    print("True negatives:", tn)
    print("False alarms:", fp)
    print("Missed defaults:", fn)
    print("Defaults flagged:", tp)
    print("Test cost units:", fp + MISSED_DEFAULT_COST * fn)