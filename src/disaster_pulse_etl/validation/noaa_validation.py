import pandas as pd

def validate_noaa_observations(
        data_df: pd.DataFrame
) -> dict:
    """
    Validate transformed NOAA GHCND observations.

    Returns:
    dict containing validation status, errors and warnings.
    """

    errors = []
    warnings = []

    if data_df.empty:
        errors.append(
            "ERROR: NOAA observations DataFrame is empty."
        )

        return {
            "status": "FAILED",
            "errors": errors,
            "warnings": warnings
        }
    
    required_columns = [
        "observation_date",
        "station_id",
        "data_type",
        "attributes",
        "value"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data_df.columns
    ]

    if missing_columns:
        errors.append(
            f"ERROR: Missing required columns: "
            f"{missing_columns}"
        )

        return {
            "status": "FAILED",
            "errors": errors,
            "warnings": warnings
        }

    if data_df["station_id"].isna().any():
            errors.append(
                "ERROR: Found observations with missing station_id."
            )

    if data_df["observation_date"].isna().any():
        errors.append(
            "ERRORS: Found observations with"
            "missing observation dates."
        )

    if data_df["data_type"].isna().any():
        errors.append(
            "ERRORS: Found observations with"
            "missing data types."
        )

    if data_df["value"].isna().any():
        errors.append(
            "ERRORS: Found observations with"
            "missing values."
        )

    duplicate_mask = data_df.duplicated(
        subset = [
            "observation_date", 
            "station_id", 
            "data_type"
            ],
        keep = False
    )

    duplicate_count = duplicate_mask.sum()

    if duplicate_count > 0:
        errors.append(
            f"ERROR: Found {duplicate_count} duplicate "
            f"observations based on observation_date, "
            f"station_id, and data_type."
        )

    missing_attributes = data_df["attributes"].isna().sum()

    if missing_attributes > 0:
        warnings.append(
            f"WARNING: Found {missing_attributes} observations "
            f"with missing attributes."
        )

    if errors:
        status = "FAILED"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASSED"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings
    }

def validate_noaa_stations(
    stations_df: pd.DataFrame
) -> dict:
    """
    Validate transformed NOAA GHCND stations data.

    Returns:
    dict containing validation status, errors and warnings.
    """

    errors = []
    warnings = []

    if stations_df.empty:
        errors.append(
            "ERROR: NOAA stations DataFrame is empty."
        )

        return {
            "status": "FAILED",
            "errors": errors,
            "warnings": warnings
        }

    if stations_df["station_id"].isna().any():
        errors.append(
            "ERROR: Found stations with missing station_id."
        )

    if stations_df["station_id"].duplicated().any():
        errors.append(
            "ERROR: Found duplicate station_id values in stations_df."
        )

    if stations_df["station_name"].isna().any():
        errors.append(
            "ERROR: Found stations with missing station_name."
        )

    if stations_df["station_latitude"].isna().any():
        errors.append(
            "ERROR: Found stations with missing or invalid station_latitude."
        )

    if stations_df["station_longitude"].isna().any():
            errors.append(
                "ERROR: Found stations with missing or invalid station_longitude."
            )

    if stations_df["station_elevation"].isna().any():
        warnings.append(
            "WARNING: Found stations with missing or invalid station_elevation."
        )

    if stations_df["station_longitude"].lt(-180).any() or stations_df["station_longitude"].gt(180).any():
        errors.append(
            "ERROR: Found stations with station_longitude "
            "outside the valid range of -180 to 180."
        )

    if stations_df["station_latitude"].lt(-90).any() or stations_df["station_latitude"].gt(90).any():
        errors.append(
            "ERROR: Found stations with station_latitude "
            "outside the valid range of -90 to 90."
        )

    if stations_df["data_coverage"].isna().any():
        errors.append(
            "ERROR: Found stations with missing or invalid data_coverage."
        )

    if stations_df["data_coverage"].lt(0).any() or stations_df["data_coverage"].gt(1).any():
        errors.append(
            "ERROR: Found stations with invalid data_coverage values."
        )

    if stations_df["minimum_date"].isna().any():
        warnings.append(
            "WARNING: Found stations with missing or invalid minimum_date."
        )

    if stations_df["maximum_date"].isna().any():
        warnings.append(
            "WARNING: Found stations with missing or invalid maximum_date."
        )

    if (
        stations_df["minimum_date"].notna() 
        & 
        stations_df["maximum_date"].notna()
        & 
        (stations_df["minimum_date"] > stations_df["maximum_date"])
    ).any():
        errors.append(
            "ERROR: Found stations where minimum_date "
            "is later than maximum_date."
        )

    if errors:
        status = "FAILED"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASSED"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings
    }

def validate_noaa_datatypes(
    type_df: pd.DataFrame
) -> dict:
    """
    Validate transformed NOAA data types.

    Returns:
    dict containing validation status, errors and warnings.
    """

    errors = []
    warnings = []

    if type_df.empty:
        errors.append(
            "ERROR: NOAA data types DataFrame is empty."
        )

        return {
            "status": "FAILED",
            "errors": errors,
            "warnings": warnings
        }

    required_columns = [
        "data_type",
        "data_type_description",
        "valid_from",
        "valid_to",
        "data_coverage"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in type_df.columns
    ]

    if missing_columns:
        errors.append(
            f"ERROR: Missing required columns: "
            f"{missing_columns}"
        )

    if type_df["data_type"].isna().any():
        errors.append(
            "ERROR: Found data types with missing "
            f"data_type."
        )

    if type_df["data_type"].duplicated().any():
        errors.append(
            "ERROR: Found duplicate data_type_id values "
            f"in type_df."
        )

    if type_df["data_type_description"].isna().any():
        warnings.append(
            "WARNING: Found data types with missing "
            f"data_type_description."
        )

    if type_df["valid_from"].isna().any():
        warnings.append(
            "WARNING: Found data types with missing or invalid "
            f"valid_from date."
        )

    if type_df["valid_to"].isna().any():
        warnings.append(
            "WARNING: Found data types with missing or invalid "
            f"valid_to date."
        )

    if (
        type_df["valid_from"].notna()
        &
        type_df["valid_to"].notna()
        &
        (type_df["valid_from"] > type_df["valid_to"])
    ).any():
        errors.append(
            "ERROR: Found data types where valid_from "
            "is later than valid_to."
        )

    if type_df["data_coverage"].isna().any():
        warnings.append(
            "WARNING: Found data types with missing or invalid "
            f"data_coverage."
        )

    if type_df["data_coverage"].lt(0).any() or type_df["data_coverage"].gt(1).any():
        warnings.append(
            "WARNING: Found data types with invalid "
            f"data_coverage values."
        )

    if errors:
        status = "FAILED"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASSED"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings
    }