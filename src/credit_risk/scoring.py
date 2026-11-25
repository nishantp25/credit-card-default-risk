from .features import build_features


def score_customer(customer_inputs, bundle):
    if len(customer_inputs) != 1:
        raise ValueError("Expected exactly one customer row.")

    features = build_features(customer_inputs)
    score = float(bundle["model"].predict_proba(features)[0, 1])
    cutoff = bundle["cutoff"]

    return score, score >= cutoff