import pandas as pd


REQUIRED_COLUMNS = [
    "source_event_id",
    "magnitude",
    "event_time",
    "updated_time",
    "latitude",
    "longitude",
    "depth_km",
    "geometry_type",
    "event_type",
    "source",
]


def validate_required_columns(df: pd.DataFrame) -> list[str]:
    """
    Check whether all required columns exist.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        return [
            f"ERROR: Missing required columns: {missing_columns}"
        ]

    return []


def validate_event_ids(df: pd.DataFrame) -> list[str]:
    """
    Check event IDs for NULLs and duplicates.
    """

    issues = []

    null_count = df["source_event_id"].isna().sum()

    if null_count > 0:
        issues.append(
            f"ERROR: source_event_id contains {null_count} NULL values."
        )

    duplicate_count = df["source_event_id"].duplicated().sum()

    if duplicate_count > 0:
        issues.append(
            f"ERROR: Found {duplicate_count} duplicate event IDs."
        )

    return issues


def validate_coordinates(df: pd.DataFrame) -> list[str]:
    """
    Validate latitude, longitude and inspect depth values.
    """

    issues = []

    invalid_latitude = ~df["latitude"].between(-90, 90)

    if invalid_latitude.any():
        count = invalid_latitude.sum()

        issues.append(
            f"ERROR: Found {count} latitude values outside [-90, 90]."
        )

    invalid_longitude = ~df["longitude"].between(-180, 180)

    if invalid_longitude.any():
        count = invalid_longitude.sum()

        issues.append(
            f"ERROR: Found {count} longitude values outside [-180, 180]."
        )

    negative_depth = df["depth_km"] < 0

    if negative_depth.any():
        count = negative_depth.sum()

        issues.append(
            f"WARNING: Found {count} negative depth values."
        )

    return issues


def validate_magnitude(df: pd.DataFrame) -> list[str]:
    """
    Validate earthquake magnitude values.
    """

    issues = []

    null_count = df["magnitude"].isna().sum()

    if null_count > 0:
        issues.append(
            f"ERROR: magnitude contains {null_count} NULL values."
        )

    return issues


def validate_earthquakes(df: pd.DataFrame) -> dict:
    """
    Run all earthquake data-quality checks and return
    a complete validation report.
    """

    issues = []

    issues.extend(validate_required_columns(df))

    # Stop only if required columns are missing because
    # subsequent checks cannot safely execute.
    if any(issue.startswith("ERROR: Missing") for issue in issues):
        return {
            "status": "FAILED",
            "errors": issues,
            "warnings": [],
        }

    issues.extend(validate_event_ids(df))
    issues.extend(validate_coordinates(df))
    issues.extend(validate_magnitude(df))

    errors = [
        issue for issue in issues
        if issue.startswith("ERROR:")
    ]

    warnings = [
        issue for issue in issues
        if issue.startswith("WARNING:")
    ]

    status = "FAILED" if errors else "PASSED"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
    }