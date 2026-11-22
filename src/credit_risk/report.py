from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve

import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from .evaluate import pr_auc

def save_calibration_chart(actual, scores):
    observed, predicted = calibration_curve(
        actual, scores, n_bins=10, strategy="quantile"
    )

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot([0, 1], [0, 1], "--", color="gray", label="Perfect calibration")
    ax.plot(predicted, observed, "o-", label="Random forest")
    ax.set(
        xlabel="Mean predicted probability of default",
        ylabel="Observed default rate",
        title="Calibration on held-out customers",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    ax.legend()

    chart_path = Path("reports/figures/calibration.png")
    chart_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(chart_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(f"Highest-risk group: predicted {predicted[-1]:.2%}, observed {observed[-1]:.2%}")
    print("Saved:", chart_path)


if __name__ == "__main__":
    predictions = pd.read_csv(Path("artifacts/test_predictions.csv"))
    actual = predictions["actual_default"]
    scores = predictions["risk_score"]

    print(f"Test default rate: {actual.mean():.2%}")
    print(f"Test ROC-AUC: {roc_auc_score(actual, scores):.4f}")
    print(f"Test PR-AUC: {pr_auc(actual, scores):.4f}")
    print(f"Test average precision: {average_precision_score(actual, scores):.4f}")
    save_calibration_chart(actual, scores)