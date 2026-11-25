from pathlib import Path

import pandas as pd
import pytest

from src.credit_risk.artifacts import load_bundle
from src.credit_risk.scoring import score_customer
from math import inf, nextafter


def test_original_example_reproduces_verified_score_and_decision():
    customer = pd.read_json(Path("examples/customer.json"))
    bundle = load_bundle()

    score, flagged = score_customer(customer, bundle)

    assert score == pytest.approx(0.11382644, abs=1e-8, rel=0)
    assert not flagged

def test_review_flag_at_the_exact_cutoff():
    customer = pd.read_json(Path("examples/customer.json"))
    bundle = load_bundle()

    # Use one worker so repeated predictions have the same summation order.
    bundle["model"].set_params(model__n_jobs=1)
    score, _ = score_customer(customer, bundle)

    bundle["cutoff"] = score
    _, flagged_at_cutoff = score_customer(customer, bundle)
    assert flagged_at_cutoff

    bundle["cutoff"] = nextafter(score, inf)
    _, flagged_below_cutoff = score_customer(customer, bundle)
    assert not flagged_below_cutoff