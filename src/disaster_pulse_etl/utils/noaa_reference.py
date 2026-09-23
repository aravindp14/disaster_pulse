from pathlib import Path
import pandas as pd

REFERENCE_PATH = Path("data/reference")

STATION_REFERENCE_PATH = REFERENCE_PATH/"station_ids.csv"

DATATYPE_REFERENCE_PATH = REFERENCE_PATH/"datatypes_ids.csv"

STATION_METADATA_PATH = REFERENCE_PATH/"station_metadata.csv"

DATATYPE_METADATA_PATH = REFERENCE_PATH/"datatype_metadata.csv"

def get_station_ids(df: pd.DataFrame) -> set[str]:
    """
    Extract unique station IDs from a DataFrame.
    """
    return set(df["station_id"].dropna())


def get_datatype_ids(df: pd.DataFrame) -> set[str]:
    """
    Extract unique datatype IDs from a DataFrame.
    """
    return set(df["data_type"].dropna())


def find_missing_stations(
    observation_station_ids: list[str] | set[str],
    existing_station_ids: set[str],
) -> set[str]:
    """
    Find station IDs present in observations but missing
    from the existing station reference.
    """
    observation_station_ids = set(observation_station_ids)

    return observation_station_ids - existing_station_ids


def find_missing_datatypes(
    observation_datatype_ids: list[str] | set[str],
    existing_datatype_ids: set[str],
) -> set[str]:
    """
    Find datatype IDs present in observations but missing
    from the existing datatype reference.
    """
    observation_datatype_ids = set(observation_datatype_ids)

    return observation_datatype_ids - existing_datatype_ids

def load_station_ids(
        station_reference_path: Path = STATION_REFERENCE_PATH
) -> set[str]:
    """
    Load station IDs from the reference CSV file.
    """

    if not station_reference_path.exists():
        return set()
    
    station_df = pd.read_csv(station_reference_path)
    return get_station_ids(station_df)

def load_datatype_ids(
        datatype_reference_path: Path = DATATYPE_REFERENCE_PATH
) -> set[str]:
    """
    Load datatype IDs from the reference CSV file.
    """

    if not datatype_reference_path.exists():
        return set()

    datatype_df = pd.read_csv(datatype_reference_path)
    datatype_df.rename(columns={"id":"data_type"},inplace=True)
    return get_datatype_ids(datatype_df)

def save_station_ids(
        station_ids: set[str],
        station_reference_path: Path = STATION_REFERENCE_PATH
) -> Path:
    """
    Save station IDs to the reference CSV file.
    """

    station_reference_path.parent.mkdir(parents=True, exist_ok=True)

    station_df = pd.DataFrame(sorted(station_ids), columns=["station_id"])
    station_df.to_csv(station_reference_path, index=False)

    return station_reference_path

def save_datatype_ids(
        datatype_ids: set[str],
        datatype_reference_path: Path = DATATYPE_REFERENCE_PATH
) -> Path:
    """
    Save datatype IDs to the reference CSV file.
    """

    datatype_reference_path.parent.mkdir(parents=True, exist_ok=True)

    datatype_df = pd.DataFrame(sorted(datatype_ids), columns=["data_type"])
    datatype_df.to_csv(datatype_reference_path, index=False)

    return datatype_reference_path

def load_station_metadata(
        path: Path = STATION_METADATA_PATH
) -> pd.DataFrame:
    """
    Load station metadata from the reference CSV file.
    """

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)

def load_datatype_metadata(
        path: Path = DATATYPE_METADATA_PATH
) -> pd.DataFrame:
    """
    Load datatype metadata from the reference CSV file.
    """

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)

def merge_station_metadata(
    current_df: pd.DataFrame,
    new_df: pd.DataFrame,
) -> pd.DataFrame:

    return pd.concat(
        [current_df, new_df],
        ignore_index=True
    )

def merge_datatype_metadata(
    current_df: pd.DataFrame,
    new_df: pd.DataFrame
) -> pd.DataFrame:

    return pd.concat(
        [current_df,new_df],
        ignore_index=True
    )
    
def save_station_metadata(
        df: pd.DataFrame,
        path: Path = STATION_METADATA_PATH
) -> Path:
    """
    Save station metadata to the reference CSV file.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)

    return path

def save_datatype_metadata(
        df: pd.DataFrame,
        path: Path = DATATYPE_METADATA_PATH
) -> Path:
    """
    Save datatype metadata to the reference CSV file.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False)

    return path

# def add_station_ids(
#     station_ids: set[str],
#     path: Path = STATION_REFERENCE_PATH,
# ) -> Path:
#     """
#     Add station IDs to the existing local station reference.
#     """
#     existing_station_ids = load_station_ids(path)

#     updated_station_ids = (
#         existing_station_ids | set(station_ids)
#     )

#     return save_station_ids(
#         updated_station_ids,
#         path,
#     )


# def add_datatype_ids(
#     datatype_ids: set[str],
#     path: Path = DATATYPE_REFERENCE_PATH,
# ) -> Path:
#     """
#     Add datatype IDs to the existing local datatype reference.
#     """
#     existing_datatype_ids = load_datatype_ids(path)

#     updated_datatype_ids = (
#         existing_datatype_ids | set(datatype_ids)
#     )

#     return save_datatype_ids(
#         updated_datatype_ids,
#         path,
#     )