import pandas as pd
import importlib.resources

datasets = [
    "adult",
    "advertising",
    "bank",
    "cereal",
    "churn",
    "churncredit",
    "churtel",
    "corona",
    "diamonds",
    "fertilizer",
    "house",
    "houseprice",
    "insurance",
    "marketing",
    "redwines",
    "risk",
    "whitewines"
]


def load(name: str) -> pd.DataFrame:
    if name in datasets:
        with importlib.resources.files("dsf.data").joinpath(f"{name}.parquet").open("rb") as f:
            return pd.read_parquet(f)
    else:
        raise ValueError(f"Dataset '{name}' does not exist.")