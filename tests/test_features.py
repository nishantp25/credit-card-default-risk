from pathlib import Path

import pandas as pd
import pytest

from src.credit_risk.features import build_features


@pytest.mark.parametrize(
    ("september_code", "expected_months", "expected_max"),
    [
        (-1, 0, 0),
        (2, 1, 2),
    ],
    ids=["original-example", "september-two-month-delay"],
)
def test_repayment_delay_features(september_code, expected_months, expected_max):
    customer = pd.read_json(Path("examples/customer.json"))
    customer.loc[0, "PAY_0"] = september_code

    features = build_features(customer)

    assert features.loc[0, "months_with_recorded_delay"] == expected_months
    assert features.loc[0, "max_recorded_delay_code"] == expected_max