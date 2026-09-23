import os
from pathlib import Path
import pandas as pd

from disaster_pulse_etl.utils.logger import get_logger

from disaster_pulse_etl.utils.csv_storage import save_processed_csv
from disaster_pulse_etl.utils.raw_storage import save_raw_json
from disaster_pulse_etl.loading.s3 import upload_to_s3

from disaster_pulse_etl.extraction.usgs import extract_earthquakes
from disaster_pulse_etl.transformation.earthquakes import transform_earthquakes
from disaster_pulse_etl.validation.earthquake_validation import validate_earthquakes


from disaster_pulse_etl.extraction.eonet import extract_eonet
from disaster_pulse_etl.transformation.eonet_events import transform_eonet
from disaster_pulse_etl.validation.eonet_validation import validate_eonet

from disaster_pulse_etl.extraction.noaa import (
    extract_noaa_data,
    extract_noaa_station,
    extract_noaa_stations,
    extract_noaa_datatypes
)

from disaster_pulse_etl.transformation.noaa_observations import (
    transform_noaa_observations,
    transform_noaa_stations,
    transform_noaa_datatypes
)

from disaster_pulse_etl.validation.noaa_validation import (
    validate_noaa_observations,
    validate_noaa_stations,
    validate_noaa_datatypes
)

from disaster_pulse_etl.utils.noaa_reference import (
    STATION_METADATA_PATH,
    DATATYPE_METADATA_PATH,
    STATION_REFERENCE_PATH,
    DATATYPE_REFERENCE_PATH,
    get_station_ids,
    get_datatype_ids,
    find_missing_stations,
    find_missing_datatypes,
    load_station_ids,
    load_datatype_ids,
    load_station_metadata,
    load_datatype_metadata,
    merge_station_metadata,
    merge_datatype_metadata,
    save_station_ids,
    save_datatype_ids,
    save_station_metadata,
    save_datatype_metadata,
)

USGS_SOURCE = "USGS"
USGS_DATASET = "earthquakes"

EONET_SOURCE = "NASA"
EONET_DATASET = "eonet"

NOAA_SOURCE = "NOAA"

NOAA_OBSERVATIONS_DATASET = "observations"
NOAA_STATIONS_DATASET = "stations"
NOAA_DATATYPES_DATASET = "datatypes"

PROCESSED_BASE_PATH = Path("data/processed")

S3_BUCKET = "disaster-pulse-etl-ak26"
S3_PREFIX = "disaster-pulse"


logger = get_logger()


def run_usgs_pipeline(
    bucket: str
) -> dict[str, str] | None:
    """
    Run the USGS earthquake ETL pipeline.

    Parameters
    ----------
    bucket: str -> Destination S3 bucket name.

    Returns
    -------
    dict[str, str] | None -> Dictionary containing output artifact paths
        when successful. Returns None when validation fails.
    """

    logger.info("Starting DisasterPulse USGS ETL pipeline")

    try:

        logger.info("Starting USGS earthquake data extraction")

        data = extract_earthquakes()

        logger.info(
            "USGS earthquake data extraction completed"
        )

        logger.info("Saving raw USGS response")

        raw_path = save_raw_json(
            data=data,
            source=USGS_SOURCE,
            dataset=USGS_DATASET
        )

        logger.info(
            "Raw USGS response saved: %s",
            raw_path
        )

        logger.info(
            "Starting USGS earthquake transformation"
        )

        df = transform_earthquakes(data)

        logger.info(
            "USGS earthquake transformation completed: "
            "%s records",
            len(df)
        )

        logger.info(
            "Starting USGS earthquake data validation"
        )

        validation_result = validate_earthquakes(df)

        for warning in validation_result["warnings"]:
            logger.warning(warning)

        for error in validation_result["errors"]:
            logger.error(error)

        if validation_result["status"] == "FAILED":
            logger.error(
                "USGS earthquake validation failed. "
                "Pipeline execution stopped."
            )
            return None

        logger.info(
            "USGS earthquake validation passed. "
            "Continuing pipeline."
        )

        logger.info(
            "Saving processed USGS earthquake data"
        )

        processed_path = save_processed_csv(
            df=df,
            source=USGS_SOURCE,
            dataset=USGS_DATASET
        )

        logger.info(
            "Processed USGS earthquake data saved: %s",
            processed_path
        )

        relative_processed_path = (
            processed_path
            .relative_to(PROCESSED_BASE_PATH.parent)
            .as_posix()
        )

        s3_key = (
            f"{S3_PREFIX}/{relative_processed_path}"
        )

        logger.info(
            "Uploading processed USGS data to S3: "
            "s3://%s/%s",
            bucket,
            s3_key
        )

        s3_uri = upload_to_s3(
            local_file=processed_path,
            bucket=bucket,
            s3_key=s3_key
        )

        logger.info(
            "Processed USGS data uploaded: %s",
            s3_uri
        )

        logger.info(
            "DisasterPulse USGS ETL pipeline "
            "completed successfully"
        )

        return {
            "raw_path": str(raw_path),
            "processed_path": str(processed_path),
            "s3_uri": s3_uri
        }

    except Exception:
        logger.exception(
            "DisasterPulse USGS ETL pipeline failed"
        )
        raise

def run_eonet_pipeline(
    bucket: str,
) -> dict[str, object] | None:
    """
    Run the NASA EONET ETL pipeline.

    Parameters
    ----------
    bucket : str
        Destination S3 bucket name.

    Returns
    -------
    dict[str, object] | None
        Dictionary containing output artifact paths
        when successful.

        Returns None when validation fails.
    """

    logger.info(
        "Starting DisasterPulse NASA EONET ETL pipeline"
    )

    try:

        logger.info(
            "Starting NASA EONET data extraction"
        )

        data = extract_eonet()

        logger.info(
            "NASA EONET data extraction completed"
        )

        logger.info(
            "Saving raw NASA EONET response"
        )

        raw_path = save_raw_json(
            data=data,
            source=EONET_SOURCE,
            dataset=EONET_DATASET
        )

        logger.info(
            "Raw NASA EONET response saved: %s",
            raw_path
        )

        logger.info(
            "Starting NASA EONET transformation"
        )

        event_df, geometry_df = transform_eonet(data)

        logger.info(
            "NASA EONET transformation completed: "
            "events=%s, geometry=%s records",
            len(event_df),
            len(geometry_df)
        )

        logger.info(
            "Starting NASA EONET data validation"
        )

        validation_result = validate_eonet(
            event_df,
            geometry_df
        )

        for warning in validation_result["warnings"]:
            logger.warning(warning)

        for error in validation_result["errors"]:
            logger.error(error)

        if validation_result["status"] == "FAILED":
            logger.error(
                "NASA EONET validation failed. "
                "Pipeline execution stopped."
            )
            return None

        logger.info(
            "NASA EONET validation passed. "
            "Continuing pipeline."
        )

        logger.info(
            "Saving processed NASA EONET event data"
        )

        processed_path_event = save_processed_csv(
            df=event_df,
            source=EONET_SOURCE,
            dataset="event"
        )

        logger.info(
            "Processed NASA EONET event data saved: %s",
            processed_path_event
        )

        logger.info(
            "Saving processed NASA EONET geometry data"
        )

        processed_path_geometry = save_processed_csv(
            df=geometry_df,
            source=EONET_SOURCE,
            dataset="geometry"
        )

        logger.info(
            "Processed NASA EONET geometry data saved: %s",
            processed_path_geometry
        )

        relative_event_path = (
            processed_path_event
            .relative_to(PROCESSED_BASE_PATH.parent)
            .as_posix()
        )

        s3_key_event = (
            f"{S3_PREFIX}/{relative_event_path}"
        )

        logger.info(
            "Uploading processed NASA EONET event data "
            "to S3: s3://%s/%s",
            bucket,
            s3_key_event
        )

        s3_uri_event = upload_to_s3(
            local_file=processed_path_event,
            bucket=bucket,
            s3_key=s3_key_event
        )

        logger.info(
            "Processed NASA EONET event data uploaded: %s",
            s3_uri_event
        )

        relative_geometry_path = (
            processed_path_geometry
            .relative_to(PROCESSED_BASE_PATH.parent)
            .as_posix()
        )

        s3_key_geometry = (
            f"{S3_PREFIX}/{relative_geometry_path}"
        )

        logger.info(
            "Uploading processed NASA EONET geometry data "
            "to S3: s3://%s/%s",
            bucket,
            s3_key_geometry
        )

        s3_uri_geometry = upload_to_s3(
            local_file=processed_path_geometry,
            bucket=bucket,
            s3_key=s3_key_geometry
        )

        logger.info(
            "Processed NASA EONET geometry data uploaded: %s",
            s3_uri_geometry
        )

        logger.info(
            "DisasterPulse NASA EONET ETL pipeline "
            "completed successfully"
        )

        return {
            "raw_path": str(raw_path),
            "processed_path": [
                str(processed_path_event),
                str(processed_path_geometry)
            ],
            "s3_uri": [
                s3_uri_event,
                s3_uri_geometry
            ]
        }

    except Exception:
        logger.exception(
            "DisasterPulse NASA EONET ETL pipeline failed"
        )
        raise

def run_noaa_pipeline(
        bucket: str
) -> dict[str, object] | None:
    """
    Run the NOAA ETL pipeline.
    """

    logger.info(
        "Starting DisasterPulse NOAA ETL pipeline"
    )

    try:
        logger.info(
            "Starting NOAA data extraction"
        )

        data = extract_noaa_data()

        logger.info(
            "NOAA data extraction completed"
        )

        logger.info(
            "Saving raw NOAA response"
        )

        raw_path = save_raw_json(
            data=data,
            source=NOAA_SOURCE,
            dataset=NOAA_OBSERVATIONS_DATASET
        )

        logger.info(
            "Raw NOAA response saved: %s",
            raw_path
        )

        logger.info(
            "Starting NOAA data transformation"
        )

        data_df = transform_noaa_observations(data)

        logger.info(
            "NOAA data transformation completed: %s records",
            data_df.shape[0]
        )

        logger.info(
            "Starting NOAA data validation"
        )

        validation_result = validate_noaa_observations(data_df)

        logger.info(
            "NOAA data validation completed: %s",
            validation_result
        )

        for warning in validation_result["warnings"]:
            logger.warning(warning)

        for error in validation_result["errors"]:
            logger.error(error)

        if validation_result["status"] == "FAILED":
            logger.error(
                "NOAA observation validation failed. "
                "Pipeline execution stopped."
            )
            return None

        if not STATION_REFERENCE_PATH.exists():

            if not bootstrap_noaa_station_reference(bucket):
                return None

        logger.info(
            "Getting observed station IDs from NOAA data"
        )

        observed_station_ids = get_station_ids(data_df)

        logger.info(
            "Observed station IDs retrieved: %s",
            len(observed_station_ids)
        )

        logger.info(
            "Getting observed data type IDs from NOAA data"
        )

        observed_datatype_ids = get_datatype_ids(data_df)

        logger.info(
            "Observed data type IDs retrieved: %s",
            len(observed_datatype_ids)
        )

        logger.info(
            "Loading existing station IDs from reference"
        )

        existing_station_ids = load_station_ids(STATION_REFERENCE_PATH)

        logger.info(
            "Existing station IDs loaded: %s",
            len(existing_station_ids)
        )

        logger.info(
            "Loading existing data type IDs from reference"
        )

        existing_datatype_ids = load_datatype_ids(DATATYPE_REFERENCE_PATH)

        logger.info(
            "Existing data type IDs loaded: %s",
            len(existing_datatype_ids)
        )

        logger.info(
            "Finding missing station IDs"
        )

        missing_station_ids = find_missing_stations(
            existing_station_ids=existing_station_ids,
            observation_station_ids=observed_station_ids
        )

        logger.info(
            "Missing station IDs found: %s",
            len(missing_station_ids)
        )

        if missing_station_ids:

            logger.info(
                "Extracting NOAA station metadata for missing station IDs"
            )

            station_records = []

            for station_id in missing_station_ids:

                logger.info(
                    "Extracting NOAA station metadata: %s",
                    station_id
                )

                station_data = extract_noaa_station(
                    station_id
                )

                station_records.append(station_data)

            station_df = transform_noaa_stations(
                {"results": station_records}
            )

            validation_result = validate_noaa_stations(
                station_df
            )

            for warning in validation_result["warnings"]:
                logger.warning(warning)

            for error in validation_result["errors"]:
                logger.error(error)

            if validation_result["status"] == "FAILED":
                logger.error(
                    "NOAA station metadata validation failed. "
                    "Pipeline execution stopped."
                )
                return None

            current_station_df = load_station_metadata(
                STATION_METADATA_PATH
            )

            updated_station_df = merge_station_metadata(
                current_df=current_station_df,
                new_df=station_df
            )

            station_metadata_path = save_station_metadata(
                df=updated_station_df
            )

            station_s3_uri = upload_to_s3(
                local_file=station_metadata_path,
                bucket=bucket,
                s3_key=(
                    f"{S3_PREFIX}/noaa/"
                    f"stations/current/stations.csv"
                )
            )

            save_station_ids(
                station_ids=get_station_ids(updated_station_df)
            )

        logger.info(
            "Finding missing data type IDs"
        )

        missing_datatype_ids = find_missing_datatypes(
            existing_datatype_ids=existing_datatype_ids,
            observation_datatype_ids=observed_datatype_ids
        )

        logger.info(
            "Missing data type IDs found: %s",
            len(missing_datatype_ids)
        )

        if missing_datatype_ids:

            logger.info(
                "Unknown NOAA datatype IDs detected: %s",
                len(missing_datatype_ids)
            )

            logger.info(
                "Extracting complete NOAA datatype catalogue"
            )

            datatype_data = extract_noaa_datatypes()

            logger.info(
                "NOAA datatype catalogue extraction completed"
            )

            logger.info(
                "Transforming NOAA datatype catalogue"
            )

            datatype_df = transform_noaa_datatypes(
                datatype_data
            )

            logger.info(
                "Transformed NOAA datatype catalogue: %s records",
                len(datatype_df)
            )

            logger.info(
                "Validating NOAA datatype catalogue"
            )

            validation_result = validate_noaa_datatypes(
                datatype_df
            )

            for warning in validation_result["warnings"]:
                logger.warning(warning)

            for error in validation_result["errors"]:
                logger.error(error)

            if validation_result["status"] == "FAILED":
                logger.error(
                    "NOAA datatype metadata validation failed. "
                    "Pipeline execution stopped."
                )
                return None

            logger.info(
                "Saving latest NOAA datatype catalogue"
            )

            datatype_metadata_path = save_datatype_metadata(
                df=datatype_df
            )

            logger.info(
                "Latest NOAA datatype catalogue saved: %s",
                datatype_metadata_path
            )

            logger.info(
                "Uploading latest NOAA datatype catalogue to S3"
            )

            datatype_s3_uri = upload_to_s3(
                local_file=datatype_metadata_path,
                bucket=bucket,
                s3_key=(
                    f"{S3_PREFIX}/noaa/"
                    f"datatypes/current/datatypes.csv"
                )
            )

            logger.info(
                "Latest NOAA datatype catalogue uploaded: %s",
                datatype_s3_uri
            )

            logger.info(
                "Updating local datatype ID reference"
            )

            save_datatype_ids(
                datatype_ids=get_datatype_ids(datatype_df)
            )

            logger.info(
                "Local datatype ID reference updated: %s",
                DATATYPE_REFERENCE_PATH
            )
            

        logger.info(
            "Saving processed NOAA observation data"
        )

        processed_path = save_processed_csv(
            df=data_df,
            source=NOAA_SOURCE,
            dataset=NOAA_OBSERVATIONS_DATASET
        )

        logger.info(
            "Processed NOAA observation data saved: %s",
            processed_path
        )

        logger.info(
            "Uploading processed NOAA observation data to S3"
        )

        relative_processed_path = (
            processed_path.relative_to(PROCESSED_BASE_PATH.parent).as_posix()
        )

        s3_key = f"{S3_PREFIX}/{relative_processed_path}"

        s3_uri = upload_to_s3(
            local_file=processed_path,
            bucket=bucket,
            s3_key=s3_key
        )

        logger.info(
            "Processed NOAA observation data uploaded to S3: %s",
            s3_uri
        )

        return {
            "raw_path": str(raw_path),
            "processed_path": str(processed_path),
            "s3_uri": s3_uri,
        }


    except Exception:
        logger.exception(
            "DisasterPulse NOAA ETL pipeline failed"
        )
        raise

def bootstrap_noaa_station_reference(bucket: str) -> bool:
    logger.info(
        "NOAA station reference not found. "
        "Bootstrapping station catalogue."
    )

    stations_data = extract_noaa_stations()

    stations_df = transform_noaa_stations(stations_data)

    validation_result = validate_noaa_stations(stations_df)

    for warning in validation_result["warnings"]:
        logger.warning(warning)

    for error in validation_result["errors"]:
        logger.error(error)

    if validation_result["status"] == "FAILED":
        logger.error(
            "NOAA station catalogue validation failed."
        )
        return False

    station_metadata_path = save_station_metadata(
            df=stations_df
        )
    
    save_station_ids(
        get_station_ids(stations_df)
    )

    logger.info(
        "NOAA station reference bootstrapped successfully: %s stations",
        len(stations_df)
    )

    upload_to_s3(
        local_file=station_metadata_path,
        bucket=bucket,
        s3_key=(
            f"{S3_PREFIX}/noaa/"
            f"stations/current/stations.csv"
        )
    )

    return True




def main() -> None:
    """
    Run all DisasterPulse ETL pipelines.

    The S3 bucket is taken from the S3_BUCKET environment
    variable. A project-level default is currently used for
    local development/testing.
    """

    bucket = S3_BUCKET

    if not bucket:
        raise ValueError(
            "S3_BUCKET is not set. "
            "Set it before running the pipeline."
        )

    logger.info(
        "Starting DisasterPulse ETL orchestration"
    )

    usgs_result = run_usgs_pipeline(
        bucket=bucket
    )

    if usgs_result is None:
        logger.error(
            "USGS pipeline completed with validation failure."
        )
    else:
        logger.info(
            "USGS pipeline completed successfully."
        )

    eonet_result = run_eonet_pipeline(
        bucket=bucket
    )

    if eonet_result is None:
        logger.error(
            "NASA EONET pipeline completed with "
            "validation failure."
        )
    else:
        logger.info(
            "NASA EONET pipeline completed successfully."
        )

    noaa_result = run_noaa_pipeline(
    bucket=bucket
    )

    if noaa_result is None:
        logger.error(
            "NOAA pipeline completed with validation failure."
        )
    else:
        logger.info(
            "NOAA pipeline completed successfully."
        )



    logger.info(
            "DisasterPulse ETL orchestration completed"
        )
    
if __name__ == "__main__":
    main()