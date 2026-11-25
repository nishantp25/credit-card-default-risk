from pathlib import Path

import pandas as pd
import streamlit as st

from src.credit_risk.artifacts import load_bundle
from src.credit_risk.features import BILL_COLUMNS, PAYMENT_COLUMNS, STATUS_COLUMNS
from src.credit_risk.scoring import score_customer


@st.cache_resource
def get_model_bundle():
    return load_bundle()


st.title("Credit Card Default Risk")
st.write(
    "Start with a real UCI example. Edit the repayment history or financial "
    "amounts, then select Calculate risk to update the score."
)

inputs = pd.read_json(Path("examples/customer.json"))
months = ["September", "August", "July", "June", "May", "April"]
status_codes = list(range(-2, 10))

with st.form("repayment_history"):
    st.subheader("Monthly repayment status")
    st.caption(
        "−1 means paid on time. Codes 1–8 give months of delay, and 9 means "
        "nine or more. UCI’s published codebook leaves −2 and 0 undefined."
    )

    for month, column in zip(months, STATUS_COLUMNS, strict=True):
        original_code = int(inputs.at[0, column])
        inputs.at[0, column] = st.selectbox(
            month,
            options=status_codes,
            index=status_codes.index(original_code),
            key=column,
        )

    with st.expander("Credit limit, bills, and payments (NT$)"):
        inputs.at[0, "LIMIT_BAL"] = st.number_input(
            "Credit limit (NT$)",
            min_value=1,
            value=int(inputs.at[0, "LIMIT_BAL"]),
            step=1,
            key="LIMIT_BAL",
        )

        bill_fields, payment_fields = st.columns(2)

        for month, bill, payment in zip(
            months, BILL_COLUMNS, PAYMENT_COLUMNS, strict=True
        ):
            inputs.at[0, bill] = bill_fields.number_input(
                f"{month} bill (NT$)",
                value=int(inputs.at[0, bill]),
                step=1,
                key=bill,
            )
            inputs.at[0, payment] = payment_fields.number_input(
                f"{month} payment (NT$)",
                min_value=0,
                value=int(inputs.at[0, payment]),
                step=1,
                key=payment,
            )

    st.form_submit_button("Calculate risk")

bundle = get_model_bundle()
score, flagged = score_customer(inputs, bundle)

st.metric("Estimated default risk", f"{score:.6%}")
st.write(f"Review cutoff: {bundle['cutoff']:.6%}")
st.write("Decision: **Flag for review**" if flagged else "Decision: **No flag**")