from pathlib import Path

import pandas as pd

from src.credit_risk.artifacts import load_bundle
from src.credit_risk.features import build_features


PROTECTED_COLUMNS = {"SEX", "MARRIAGE", "AGE"}


def test_adding_audit_columns_leaves_model_features_unchanged():
    customer = pd.read_json(Path("examples/customer.json"))
    expected = build_features(customer)

    # Empty audit fields exercise the schema without inventing customer details.
    customer_with_audit = customer.assign(SEX=pd.NA, MARRIAGE=pd.NA, AGE=pd.NA)
    actual = build_features(customer_with_audit)

    assert PROTECTED_COLUMNS.isdisjoint(actual.columns)
    pd.testing.assert_frame_equal(actual, expected)


def test_saved_pipeline_was_fitted_without_protected_columns():
    model = load_bundle()["model"]
    fitted_columns = set(model.feature_names_in_)

    leaked_columns = PROTECTED_COLUMNS & fitted_columns
    assert not leaked_columns, f"Protected columns seen during fit: {leaked_columns}"