import pandas as pd
from datetime import datetime


def transform_earthquakes(data: dict) -> pd.DataFrame:
    """
    Transform raw USGS GeoJSON data into a source-complete
    tabular representation.

    The goal of this stage is to preserve the useful attributes
    provided by USGS while flattening the nested GeoJSON structure.

    Parameters
    ------------
    data: dict -> Raw USGS GeoJSON response.

    Returns
    ------------
    pd.DataFrame -> Source-complete staging DataFrame.
    """

    records = []

    for feature in data.get("features", []):

        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [])

        record = {
            # Feature-level attributes
            "feature_type": feature.get("type"),
            "source_event_id": feature.get("id"),

            # Properties
            "magnitude": properties.get("mag"),
            "place": properties.get("place"),
            "event_time": properties.get("time"),
            "updated_time": properties.get("updated"),
            "timezone_offset": properties.get("tz"),
            "event_url": properties.get("url"),
            "detail_url": properties.get("detail"),
            "felt_reports": properties.get("felt"),
            "cdi": properties.get("cdi"),
            "mmi": properties.get("mmi"),
            "alert_level": properties.get("alert"),
            "event_status": properties.get("status"),
            "tsunami_flag": properties.get("tsunami"),
            "significance": properties.get("sig"),
            "network": properties.get("net"),
            "source_code": properties.get("code"),
            "associated_event_ids": properties.get("ids"),
            "associated_sources": properties.get("sources"),
            "associated_types": properties.get("types"),
            "station_count": properties.get("nst"),
            "minimum_distance": properties.get("dmin"),
            "rms": properties.get("rms"),
            "azimuthal_gap": properties.get("gap"),
            "magnitude_type": properties.get("magType"),
            "event_type": properties.get("type"),
            "title": properties.get("title"),

            # Geometry
            "geometry_type": geometry.get("type"),
            "longitude": coordinates[0] if len(coordinates) > 0 else None,
            "latitude": coordinates[1] if len(coordinates) > 1 else None,
            "depth_km": coordinates[2] if len(coordinates) > 2 else None,

            # Pipeline metadata
            "source": "USGS",
            "ingested_at": datetime.now(),
        }

        records.append(record)

    df = pd.DataFrame(records)

    df['event_time'] = pd.to_datetime(
        df['event_time'],
        unit='ms',
        utc=True
    )

    df['updated_time'] = pd.to_datetime(
        df['updated_time'],
        unit="ms",
        utc=True
    )

    df['ingested_at'] = pd.Timestamp.now(tz="UTC")

    df["felt_reports"] = df["felt_reports"].astype("Int64")
    df["station_count"] = df["station_count"].astype("Int64")
    df["significance"] = df["significance"].astype("Int64")

    return df