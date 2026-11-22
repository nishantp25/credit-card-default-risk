from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier

from .features import BILL_COLUMNS, PAYMENT_COLUMNS, STATUS_COLUMNS


def _build_pipeline(classifier) -> Pipeline:
    numeric_columns = (
        ["LIMIT_BAL"]
        + BILL_COLUMNS
        + PAYMENT_COLUMNS
        + ["months_with_recorded_delay", "max_recorded_delay_code"]
    )

    preprocess = ColumnTransformer([
        ("status", OneHotEncoder(handle_unknown="ignore"), STATUS_COLUMNS),
        ("numeric", StandardScaler(), numeric_columns),
    ])

    return Pipeline([
        ("preprocess", preprocess),
        ("model", classifier),
    ])

def build_logistic_pipeline() -> Pipeline:
    return _build_pipeline(LogisticRegression(max_iter=1000))


def build_forest_pipeline() -> Pipeline:
    forest = RandomForestClassifier(
        n_estimators=200,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )
    return _build_pipeline(forest)

def build_boosting_pipeline() -> Pipeline:
    boosting = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=2,
        random_state=42,
    )
    return _build_pipeline(boosting)