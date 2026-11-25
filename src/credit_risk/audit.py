from pathlib import Path

import pandas as pd

from .data import load_clients


def summarize_errors(audit, group_column):
    defaulted = audit["actual_default"].eq(1)
    flagged = audit["flagged"]

    outcomes = audit.assign(
        false_alarm=flagged & ~defaulted,
        missed_default=~flagged & defaulted,
    )

    summary = outcomes.groupby(group_column, dropna=False).agg(
        customers=("ID", "size"),
        flagged=("flagged", "sum"),
        defaults=("actual_default", "sum"),
        false_alarms=("false_alarm", "sum"),
        missed_defaults=("missed_default", "sum"),
    )

    defaults = summary["defaults"]
    non_defaults = summary["customers"] - defaults
    summary["non_defaults"] = non_defaults

    # A rate is undefined when its group has no customers in the denominator.
    summary["flag_rate"] = summary["flagged"] / summary["customers"]
    summary["false_alarm_rate"] = (
        summary["false_alarms"] / non_defaults.where(non_defaults > 0)
    )
    summary["missed_default_rate"] = (
        summary["missed_defaults"] / defaults.where(defaults > 0)
    )

    return summary


if __name__ == "__main__":
    predictions = pd.read_csv(
        Path("artifacts/test_predictions.csv"),
        dtype={"flagged": "boolean"},
    )
    clients = load_clients(Path("data/raw/default of credit card clients.xls"))
    demographics = clients[["ID", "SEX", "MARRIAGE", "AGE"]]

    audit = predictions.merge(
        demographics,
        on="ID",
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    print("Test predictions:", len(audit))
    print("Unmatched IDs:", audit["_merge"].ne("both").sum())

    sex_summary = summarize_errors(audit, "SEX")
    print(sex_summary.to_string(float_format="{:.2%}".format))

    print("Total flagged:", sex_summary["flagged"].sum())
    print("Total false alarms:", sex_summary["false_alarms"].sum())
    print("Total missed defaults:", sex_summary["missed_defaults"].sum())
    marriage_summary = summarize_errors(audit, "MARRIAGE")
    print("\nAudit by marital status")
    print(marriage_summary.to_string(float_format="{:.2%}".format))
    audit["age_band"] = pd.cut(
        audit["AGE"],
        bins=[float("-inf"), 30, 40, 50, 60, float("inf")],
        labels=["Under 30", "30–39", "40–49", "50–59", "60+"],
        right=False,
    )

    age_summary = summarize_errors(audit, "age_band")
    print("\nAudit by age band")
    print(age_summary.to_string(float_format="{:.2%}".format))