import pandas as pd
import importlib.resources

def load(name: str) -> pd.DataFrame:
    with importlib.resources.files("dsf.data").joinpath(f"{name}.parquet").open("rb") as f:
        return pd.read_parquet(f)