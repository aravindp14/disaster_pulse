import pandas as pd
from datetime import datetime

def transform_eonet(data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Transform raw EONET GeoJSON data into a source-complete
    tabular representation.

    The goal of this stage is to prepare the useful attributes
    provided by NASA EONET while flattening the nested GeoJSON 
    structure.

    Parameters
    ------------
    data: dict -> Raw EONET GeoJSON response.

    Returns
    ------------
    events_df: one row per unique EONET event.
    geometry_df: one row per spatial observation.
    """

    event_records = []
    geometry_records = []
    seen_event_ids = set()

    for feature in data.get("features",[]):

        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        categories = properties.get("categories", [])
        category = categories[0] if categories else {}

        sources = properties.get("sources", [])
        source = sources[0] if sources else {}

        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates")

        event_record = {
            "event_id": properties["id"],
            "title": properties.get("title"),
            "description": properties.get("description"),
            "event_url": properties.get("link"),
            "event_date": properties.get("date"),
            "closed_at": properties.get("closed"),
            "category_id": category.get("id"),
            "category_title": category.get("title"),
            "source_id": source.get("id"),
            "source_url": source.get("url"),
            "magnitude_value": properties.get("magnitudeValue"),
            "magnitude_unit": properties.get("magnitudeUnit"),
        }

        if properties["id"] not in seen_event_ids:
            event_records.append(event_record)
            seen_event_ids.add(properties["id"])

        if geometry_type == "Point":
            geometry_records.append(
                {
                    "event_id": properties["id"],
                    "observation_sequence": 1,
                    "geometry_date": properties.get("date"),
                    "geometry_type": geometry_type,
                    "longitude": coordinates[0],
                    "latitude": coordinates[1],
                    "geometry": coordinates,
                }
            )
        elif geometry_type == "LineString":
            geometry_dates = properties.get("geometryDates", [])

            if len(geometry_dates) != len(coordinates):
                raise ValueError(
                    f"Geometry date/coordinate mismatch for "
                    f"event {properties['id']}: "
                    f"{len(geometry_dates)} dates vs "
                    f"{len(coordinates)} coordinates"
                )

            for i, coordinate in enumerate(coordinates):
                geometry_records.append(
                    {
                        "event_id": properties["id"],
                        "observation_sequence": i + 1,
                        "geometry_date": geometry_dates[i],
                        "geometry_type": geometry_type,
                        "longitude": coordinate[0],
                        "latitude": coordinate[1],
                        "geometry": coordinate,
                    }
                )
        elif geometry_type == "Polygon":
            geometry_records.append(
                {
                    "event_id": properties["id"],
                    "observation_sequence": 1,
                    "geometry_date": properties.get("date"),
                    "geometry_type": geometry_type,
                    "longitude": None,
                    "latitude": None,
                    "geometry": coordinates,
                }
            )
        else:
            raise ValueError(
                f"Unsupported EONET geometry type: {geometry_type}"
            )

    events_df = pd.DataFrame(event_records)
    geometry_df = pd.DataFrame(geometry_records)

    geometry_df["geometry_date"] = pd.to_datetime(
        geometry_df["geometry_date"],
        errors="coerce",
        utc=True
    )

    events_df["event_date"] = pd.to_datetime(
        events_df["event_date"],
        errors="coerce",
        utc=True
    )

    events_df["closed_at"] = pd.to_datetime(
        events_df["closed_at"],
        errors="coerce",
        utc=True
    )

    return events_df, geometry_df

