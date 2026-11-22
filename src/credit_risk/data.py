from pathlib import Path

import pandas as pd


def load_clients(workbook: Path) -> pd.DataFrame:
    # The first Excel row contains X1–X23 codes. The second has the column names.
    return pd.read_excel(workbook, header=1)