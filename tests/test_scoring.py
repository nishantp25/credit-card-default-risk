from pathlib import Path

import pandas as pd
import pytest

from src.credit_risk.artifacts import load_bundle
from src.credit_risk.scoring import score_customer


def test_original_example_reproduces_verified_score_and_decision():
    customer = pd.read_json(Path("examples/customer.json"))
    bundle = load_bundle()

    score, flagged = score_customer(customer, bundle)

    assert score == pytest.approx(0.11382644, abs=1e-8, rel=0)
    assert not flagged