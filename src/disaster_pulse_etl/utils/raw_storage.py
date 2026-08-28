import json
from datetime import datetime
from pathlib import Path

def save_raw_json(
        data: dict,
        source: str,
        dataset: str,
        base_path: str = "data/raw"
) -> Path:
    """
    Save raw API response as a timestamp JSON file.

    Parameters
    ------------
    data:dict - Raw API response
    source: str - Data Source name, e.g. 'usgs'
    dataset: str - dataset name, e.g. 'earthquakes'
    base_path: str - Root directory for raw data

    Returns
    ------------
    Path - Path to the saved JSON file
    """

    extraction_time = datetime.now()

    output_dir = (
        Path(base_path)
        / source
        / dataset
        / extraction_time.strftime("%Y")
        / extraction_time.strftime("%m")
        / extraction_time.strftime("%d")
    )

    output_dir.mkdir(parents=True,exist_ok=True)

    filename = f"{dataset}_{extraction_time.strftime('%H%M%S')}.json"

    output_path = output_dir / filename

    with output_path.open("w",encoding="utf-8") as file:
        json.dump(data,file,indent=2)

    return output_path