from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

def save_processed_csv(
        df: pd.DataFrame,
        source: str,
        dataset: str,
        base_path: str = "data/processed"
) -> Path:

    """
    Save a transformed DataFrame as a timestamp CSV file.
    
    Parameter
    ------------
    df: pd.DataFrame -> Validated dataframe.
    source: str -> source name, e.g. "usgs".
    dataset: str -> dataset name, e.g. "earthquake".
    base_path: str -> root directory for processed data

    Returns
    ------------
    Path -> path to the saved CSV file

    """

    extraction_time = datetime.now(timezone.utc)

    output_dir = (
        Path(base_path)
        /source
        /dataset
        /f"{extraction_time:%Y-%m-%d}"
    )

    output_dir.mkdir(parents=True,exist_ok=True)

    filename = (
        f"{dataset}_{extraction_time:%Y%m%dT%H%M%SZ}.csv"
    )

    output_path = output_dir / filename

    df.to_csv(
        output_path,
        index=False
    )

    return output_path