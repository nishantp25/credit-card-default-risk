from io import BytesIO
from pathlib import Path
from shutil import copyfileobj
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.request import urlopen
from zipfile import ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = PROJECT_ROOT / "data" / "raw" / "default of credit card clients.xls"
PREDICTIONS = PROJECT_ROOT / "artifacts" / "test_predictions.csv"
DATASET_URL = (
    "https://archive.ics.uci.edu/static/public/350/"
    "default%2Bof%2Bcredit%2Bcard%2Bclients.zip"
)


def ensure_workbook():
    if WORKBOOK.is_file():
        return

    print("Downloading the original UCI workbook...", flush=True)
    WORKBOOK.parent.mkdir(parents=True, exist_ok=True)

    with urlopen(DATASET_URL, timeout=60) as response:
        archive_bytes = response.read()

    with ZipFile(BytesIO(archive_bytes)) as archive:
        member = next(
            name for name in archive.namelist()
            if Path(name).name == WORKBOOK.name
        )

        # Publish the workbook only after extraction finishes successfully.
        with TemporaryDirectory(dir=WORKBOOK.parent) as temp_dir:
            temp_workbook = Path(temp_dir) / WORKBOOK.name
            with archive.open(member) as source, temp_workbook.open("wb") as target:
                copyfileobj(source, target)
            temp_workbook.replace(WORKBOOK)


def run_module(name):
    subprocess.run(
        [sys.executable, "-m", f"src.credit_risk.{name}"],
        cwd=PROJECT_ROOT,
        check=True,
    )


def main():
    ensure_workbook()

    if not PREDICTIONS.is_file():
        print("Generating test predictions with the saved model...", flush=True)
        run_module("holdout")

    run_module("audit")


if __name__ == "__main__":
    main()