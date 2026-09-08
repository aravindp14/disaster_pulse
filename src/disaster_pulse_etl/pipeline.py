import os
from pathlib import Path

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


USGS_SOURCE = "USGS"
USGS_DATASET = "earthquakes"

EONET_SOURCE = "NASA"
EONET_DATASET = "eonet"

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

    logger.info(
        "DisasterPulse ETL orchestration completed"
    )


if __name__ == "__main__":
    main()