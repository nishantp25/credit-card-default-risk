from pathlib import Path
from sklearn.model_selection import train_test_split
import pandas as pd


def load_clients(workbook: Path) -> pd.DataFrame:
    # The first Excel row contains X1–X23 codes. The second has the column names.
    return pd.read_excel(workbook, header=1)

def split_clients(clients: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    target = "default payment next month"

    development, test = train_test_split(
        clients,
        test_size=0.20,
        stratify=clients[target],
        random_state=42,
    )

    train, validation = train_test_split(
        development,
        test_size=0.25,
        stratify=development[target],
        random_state=42,
    )

    return train, validation, test