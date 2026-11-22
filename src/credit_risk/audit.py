from pathlib import Path

import pandas as pd

from .data import load_clients


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

    sex_summary = audit.groupby("SEX", dropna=False).agg(
        customers=("ID", "size"),
        flagged=("flagged", "sum"),
        flag_rate=("flagged", "mean"),
    )

    print(sex_summary.to_string(float_format="{:.2%}".format))
    print("Total flagged:", sex_summary["flagged"].sum())