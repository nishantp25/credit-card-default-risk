import pandas as pd


STATUS_COLUMNS = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
BILL_COLUMNS = [f"BILL_AMT{i}" for i in range(1, 7)]
PAYMENT_COLUMNS = [f"PAY_AMT{i}" for i in range(1, 7)]

MODEL_INPUT_COLUMNS = ["LIMIT_BAL"] + STATUS_COLUMNS + BILL_COLUMNS + PAYMENT_COLUMNS


def select_model_inputs(clients: pd.DataFrame) -> pd.DataFrame:
    return clients.loc[:, MODEL_INPUT_COLUMNS].copy()

def build_features(clients: pd.DataFrame) -> pd.DataFrame:
    features = select_model_inputs(clients)
    recorded_delays = features[STATUS_COLUMNS].isin(range(1, 10))
    features["months_with_recorded_delay"] = recorded_delays.sum(axis="columns")
    delay_codes = features[STATUS_COLUMNS].where(recorded_delays, 0)
    features["max_recorded_delay_code"] = delay_codes.max(axis="columns")
    return features