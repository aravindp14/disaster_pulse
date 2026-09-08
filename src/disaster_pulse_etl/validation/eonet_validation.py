import pandas as pd

def validate_eonet(
        events_df: pd.DataFrame,
        geometry_df: pd.DataFrame
) -> dict:
    """
    Validate transformed NASA EONET event and geometry data.

    Returns:
    dict containing validation status, errors and warnings.
    """

    # Event ID validation

    errors = []
    warnings = []

    if events_df["event_id"].isna().any():
        errors.append(
            "ERROR: Found events with missing event id."
        )

    if not events_df["event_id"].is_unique:
        errors.append(
            "ERROR: event_id is not unique in events_df."
        )

    # Required event columns validation

    required_event_columns = [
        "event_id",
        "title",
        "event_url",
        "event_date",
        "category_id"
    ]

    missing_event_columns = [
        column
        for column in required_event_columns
        if column not in events_df.columns
    ]

    if missing_event_columns:
        errors.append(
            f"ERROR: Missing event columns: "
            f"{missing_event_columns}"
        )

    # Event date validation

    if "event_date" in events_df.columns:

        invalid_event_dates = (pd.to_datetime(
            events_df["event_date"],
            errors="coerce",
            utc=True
        ).isna() & events_df["event_date"].notna())

        if invalid_event_dates.any():
            errors.append(
                f"ERROR: Found "
                f"{invalid_event_dates.sum()} invalid event dates."
            )

        missing_event_dates = events_df["event_date"].isna().sum()

        if missing_event_dates > 0:
            warnings.append(
                f"WARNING: Found "
                f"{missing_event_dates.sum()} invalid event dates."
            )

    # Closing Date Validation

    if "closed_at" in events_df.columns:

        invalid_closed_dates = (pd.to_datetime(
            events_df["closed_at"],
            errors="coerce",
            utc=True
        ).isna() & events_df["closed_at"].notna())

        if invalid_closed_dates.any():
            errors.append(
                f"ERROR: Found "
                f"{invalid_closed_dates.sum()} invalid closed_at dates."
            )

    # Category Validation

    if "category_id" in events_df.columns:

        missing_categories = events_df["category_id"].isna().sum()

        if missing_categories > 0:
            warnings.append(
                f"WARNING: Found "
                f"{missing_categories} events with missing category."
            )

    # Geometry Type Validation

    valid_geometry_types = {
        "Point",
        "LineString",
        "Polygon"
    }

    if "geometry_type" in geometry_df.columns:

        invalid_geometry_types = geometry_df[~geometry_df["geometry_type"].isin(valid_geometry_types)]["geometry_type"].to_list()

        if invalid_geometry_types:
            errors.append(
                f"ERROR: Found "
                f"unsupported geometry types: "
                f"{set(invalid_geometry_types)}"
            )

    # Latitude validation

    if "latitude" in geometry_df.columns:

        invalid_latitudes = (
            geometry_df["latitude"].notna()
            & ~ geometry_df["latitude"].between(-90,90)
        )

        if invalid_latitudes.any():
            errors.append(
                f"ERROR: Found "
                f"{invalid_latitudes.sum()} invalid latitude values."
            )

    # Longitude validation

    if "longitude" in geometry_df.columns:

        invalid_longitudes = (
            geometry_df["longitude"].notna()
            & ~geometry_df["longitude"].between(-180, 180)
        )

        if invalid_longitudes.any():
            errors.append(
                f"ERROR: Found "
                f"{invalid_longitudes.sum()} invalid longitude values."
            )

    # Geometry Event ID

    if (
        "event_id" in geometry_df.columns
        and "event_id" in events_df.columns
    ):

        event_ids = set(events_df["event_id"])

        orphan_geometry = geometry_df[~geometry_df["event_id"].isin(event_ids)]["event_id"].to_list()

        if orphan_geometry:
            errors.append(
                f"ERROR: Found "
                f"geometry records "
                f"without a matching event_id: "
                f"{set(orphan_geometry)}"                
            )

    # observation sequence validation

    if "observation_sequence" in geometry_df.columns:

        missing_sequence = (
            geometry_df["observation_sequence"].isna()
        )

        if missing_sequence.any():
            errors.append(
                f"ERROR: Found "
                f"{missing_sequence.sum()} geometry records "
                f"with missing observation sequence."
            )

        invalid_sequence = (
            geometry_df["observation_sequence"].notna()
            & (geometry_df["observation_sequence"] < 1)
        )

        if invalid_sequence.any():
            errors.append(
                f"ERROR: Found "
                f"{invalid_sequence.sum()} invalid "
                f"observation sequence "
            )

    # Geometry Date Validation

    if "geometry_date" in geometry_df.columns:

        invalid_geometry_dates = (pd.to_datetime(
            geometry_df["geometry_date"],
            errors="coerce",
            utc=True
        ).isna() & geometry_df["geometry_date"].notna())

        if invalid_geometry_dates.any():
            errors.append(
                f"ERROR: Found "
                f"{invalid_geometry_dates.sum()} invalid "
                f"geometry_dates values."
            )

        missing_geometry_dates = (
            geometry_df["geometry_date"].isna().sum()
        )

        if missing_geometry_dates > 0:
            warnings.append(
                f"WARNING: Found "
                f"{missing_geometry_dates} geometry records "
                f"with missing geometry_dates"
            )

    # Empty Data Frame Check

    if events_df.empty:
        errors.append(
            "ERROR: events_df contains no records."
        )

    if geometry_df.empty:
        errors.append(
            "ERROR: geometry_df contains no records."
        )

    if errors:
        status = "FAILED"
    elif warnings:
        status = "PASSED_WITH_WARNINGS"
    else:
        status = "PASSED"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings
    }