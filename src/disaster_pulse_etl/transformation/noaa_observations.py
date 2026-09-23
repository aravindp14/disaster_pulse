import pandas as pd

def transform_noaa_observations(
    data:dict
) -> pd.DataFrame:
    """
    Transform raw NOAA GHCHD observations into
    a standardized tabular structure.

    Parameters
    ------------
    data: dict
        Raw NOAA API response.

    Returns
    ------------
    pd.DataFrame
        Transformed NOAA observation data.
    """

    results = data.get("results", [])

    df = pd.DataFrame(results)

    if df.empty:
        return df

    df = df.rename(
        columns={
            "date":"observation_date",
            "station":"station_id",
            "datatype":"data_type",
            "attributes":"attributes",
            "value":"value"
        }
    )

    df["observation_date"] = pd.to_datetime(
        df["observation_date"],
        errors = "coerce",
        utc = True
    )

    df["station_id"] = df["station_id"].astype("string")
    df["data_type"] = df["data_type"].astype("string")
    df["attributes"] = df["attributes"].astype("string")
    df["value"] = pd.to_numeric(df["value"],errors="coerce")

    return df

def transform_noaa_stations(
    data:dict
) -> pd.DataFrame:
    """
    Transform raw NOAA GHCND stations data into
    a standardized tabular structure.

    Parameters
    ------------
    data: dict
        Raw NOAA API response.

    Returns
    ------------
    pd.DataFrame
        Transformed NOAA stations data.
    """

    results = data.get("results",[])

    df = pd.DataFrame(results)

    if df.empty:
        return df

    df = df.rename(
        columns={
            "elevation":"station_elevation",
            "mindate":"minimum_date",
            "maxdate": "maximum_date",
            "latitude": "station_latitude",
            "name": "station_name",
            "datacoverage": "data_coverage",
            "id": "station_id",
            "elevationUnit": "station_elevation_unit",
            "longitude": "station_longitude"
        } 
    )

    df["minimum_date"] = pd.to_datetime(
        df["minimum_date"],
        errors="coerce",
        utc=True
    )
    
    df["maximum_date"] = pd.to_datetime(
        df["maximum_date"],
        errors="coerce",
        utc=True
    )

    
    df["station_latitude"] = df["station_latitude"].astype("Float64")
    df["station_longitude"] = df["station_longitude"].astype("Float64")
    df["station_name"] = df["station_name"].astype("string")
    df["data_coverage"] = df["data_coverage"].astype("Float64")
    df["station_id"] = df["station_id"].astype("string")
    df["station_elevation"] = df["station_elevation"].astype("Float64")
    df["station_elevation_unit"] = df["station_elevation_unit"].astype("string")

    return df
    
    
def transform_noaa_datatypes(
    data:dict
) -> pd.DataFrame:
    """
    Transform raw NOAA data types into
    a standardized tabular structure.

    Parameters
    ------------
    data: dict
        Raw NOAA API response.

    Returns
    ------------
    pd.DataFrame
        Transformed NOAA data types.
    """

    results = data.get("results",[])

    df = pd.DataFrame(results)

    if df.empty:
        return df

    df = df.rename(
        columns={
            "mindate":"valid_from",
            "maxdate":"valid_to",
            "name":"data_type_description",
            "datacoverage":"data_coverage",
            "id":"data_type"
        }
    )

    df["valid_from"] = pd.to_datetime(
        df["valid_from"],
        errors="coerce",
        utc=True
    )

    df["valid_to"] = pd.to_datetime(
        df["valid_to"],
        errors="coerce",
        utc=True
    )

    df["data_coverage"] = pd.to_numeric(
        df["data_coverage"],
        errors="coerce"
    )

    df["data_type_description"] = df["data_type_description"].astype("string")
    
    df["data_type"] = df["data_type"].astype("string")

    return df