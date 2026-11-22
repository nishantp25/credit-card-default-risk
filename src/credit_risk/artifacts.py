import pickle
from pathlib import Path


BUNDLE_PATH = Path("artifacts/credit_default_model.pkl")


def save_bundle(model, cutoff):
    BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BUNDLE_PATH.open("wb") as file:
        pickle.dump({"model": model, "cutoff": float(cutoff)}, file)


def load_bundle():
    with BUNDLE_PATH.open("rb") as file:
        return pickle.load(file)