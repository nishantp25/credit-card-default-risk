from pathlib import Path
from sklearn.metrics import confusion_matrix, confusion_matrix_at_thresholds

from .data import load_clients, split_clients
from .features import build_features
from .modeling import build_forest_pipeline

MISSED_DEFAULT_COST = 5

def cost_at_cutoff(y_true, scores, cutoff):
    flagged = scores >= cutoff
    _, false_alarms, missed_defaults, _ = confusion_matrix(
        y_true, flagged, labels=[0, 1]
    ).ravel()

    cost = false_alarms + MISSED_DEFAULT_COST * missed_defaults
    return false_alarms, missed_defaults, cost

def choose_cutoff(y_true, scores):
    _, false_alarms, missed_defaults, true_positives, cutoffs = (
        confusion_matrix_at_thresholds(y_true, scores, pos_label=1)
    )

    costs = false_alarms + MISSED_DEFAULT_COST * missed_defaults
    best = costs.argmin()

    total_defaults = true_positives[-1]
    cost_if_no_flags = MISSED_DEFAULT_COST * total_defaults
    if cost_if_no_flags <= costs[best]:
        return float("inf")

    return float(cutoffs[best])


if __name__ == "__main__":
    clients = load_clients(Path("data/raw/default of credit card clients.xls"))
    train, validation, _ = split_clients(clients)
    target = "default payment next month"

    model = build_forest_pipeline()
    model.fit(build_features(train), train[target])

    scores = model.predict_proba(build_features(validation))[:, 1]
    false_alarms, missed_defaults, cost = cost_at_cutoff(
        validation[target], scores, cutoff=0.50
    )

    print("Validation customers:", len(scores))
    print("False alarms:", false_alarms)
    print("Missed defaults:", missed_defaults)
    print("Cost units at 0.50:", cost)
    best_cutoff = choose_cutoff(validation[target], scores)
    best_false_alarms, best_missed_defaults, best_cost = cost_at_cutoff(
        validation[target], scores, best_cutoff
    )

    print("\nSelected cutoff:", best_cutoff)
    print("False alarms at selected cutoff:", best_false_alarms)
    print("Missed defaults at selected cutoff:", best_missed_defaults)
    print("Cost units at selected cutoff:", best_cost)
    print("Validation cost reduction:", cost - best_cost)