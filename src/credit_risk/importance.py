from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score

from .artifacts import load_bundle
from .data import load_clients, split_clients
from .features import build_features, select_model_inputs


def score_raw_inputs(model, raw_inputs, actual):
    features = build_features(raw_inputs)
    scores = model.predict_proba(features)[:, 1]
    return average_precision_score(actual, scores)

if __name__ == "__main__":
    clients = load_clients(Path("data/raw/default of credit card clients.xls"))
    _, validation, _ = split_clients(clients)
    raw_inputs = select_model_inputs(validation)
    model = load_bundle()["model"]

    result = permutation_importance(
        model,
        raw_inputs,
        validation["default payment next month"],
        scoring=score_raw_inputs,
        n_repeats=5,
        random_state=42,
    )

    importance = pd.Series(result.importances_mean, index=raw_inputs.columns)
    top_ten = importance.nlargest(10)

    fig, ax = plt.subplots(figsize=(7, 5))
    top_ten.sort_values().plot.barh(ax=ax)
    ax.set_title("Random forest input importance on validation customers")
    ax.set_xlabel("Mean decrease in average precision after shuffling")
    fig.tight_layout()

    chart_path = Path("reports/figures/permutation_importance.png")
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)

    print(top_ten.head(5).round(4).to_string())
    print("Saved:", chart_path)