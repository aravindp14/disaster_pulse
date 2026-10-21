import pandas as pd

REQUIRED_COLUMNS = [
        "country_iso3_code",
        "year",
        "population",
        "country_id",
        "country_name"
    ]

def validate_required_columns(
        df: pd.DataFrame
        ) -> list[str]:

    """
    Validate the population data DataFrame to ensure it meets the expected schema and data quality standards.
    """

    

    missing_columns = [
        col 
        for col in REQUIRED_COLUMNS 
        if col not in df.columns
    ]

    if missing_columns:
        return [f"ERROR: Missing required columns: {', '.join(missing_columns)}"]

    return []

def validate_country_ids(
        df: pd.DataFrame
        ) -> list[str]:

    """
    Validate the country IDs in the DataFrame to ensure they meet the expected schema and data quality standards.
    """
    
    issues = []

    null_count = df["country_id"].isna().sum()

    if null_count > 0:
        issues.append(
            f"ERROR: country_id contains {null_count} NULL values."
        )

    duplicate_count = df[["country_id", "year"]].duplicated().sum()

    if duplicate_count > 0:
        issues.append(
            f"ERROR: Found {duplicate_count} duplicate records with the same country_id and year."
        )

    return issues

def validate_population_values(
        df: pd.DataFrame
        ) -> list[str]:

    """
    Validate the population values in the DataFrame to ensure they meet the expected schema and data quality standards.
    """

    issues = []
    
    if df["population"].isnull().any():
        issues.append("WARNING: Population column contains null values.")

    if not pd.api.types.is_numeric_dtype(df["population"]):
        issues.append("ERROR: Population column is not numeric.")

    if df["population"].dropna().lt(0).any():
        issues.append("ERROR: Population column contains negative values.")
    
    return issues

def validate_world_bank(
        df: pd.DataFrame
        ) -> list[str]:

    """
    Validate the World Bank population data DataFrame to ensure it meets the expected schema and data quality standards.
    """

    issues = []

    issues.extend(validate_required_columns(df))

    if any(issue.startswith("ERROR: Missing") for issue in issues):
        return {
            "status": "FAILED",
            "errors": issues,
            "warnings": [],
        }
    
    issues.extend(validate_country_ids(df))
    issues.extend(validate_population_values(df))

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
        "warnings": warnings
    }
