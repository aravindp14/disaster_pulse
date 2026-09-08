[1mdiff --git a/.gitignore b/.gitignore[m
[1mindex c428b8d..233be37 100644[m
[1m--- a/.gitignore[m
[1m+++ b/.gitignore[m
[36m@@ -16,6 +16,11 @@[m [mdist/[m
 build/[m
 *.egg-info/[m
 [m
[32m+[m[32m# Python tooling[m
[32m+[m[32m.pyright/[m
[32m+[m[32m.mypy_cache/[m
[32m+[m[32m.ruff_cache/[m
[32m+[m
 [m
 # ============================================================[m
 # Environment & Secrets[m
[1mdiff --git a/src/disaster_pulse_etl/loading/s3.py b/src/disaster_pulse_etl/loading/s3.py[m
[1mindex af8f5b3..986d82e 100644[m
[1m--- a/src/disaster_pulse_etl/loading/s3.py[m
[1m+++ b/src/disaster_pulse_etl/loading/s3.py[m
[36m@@ -36,6 +36,6 @@[m [mdef upload_to_s3([m
         s3_key[m
     )[m
 [m
[31m-    s3_uri = f"s3//{bucket}//{s3_key}"[m
[32m+[m[32m    s3_uri = f"s3//{bucket}/{s3_key}"[m
 [m
     return s3_uri[m
\ No newline at end of file[m
[1mdiff --git a/src/disaster_pulse_etl/pipeline.py b/src/disaster_pulse_etl/pipeline.py[m
[1mindex 293f530..7ac31a3 100644[m
[1m--- a/src/disaster_pulse_etl/pipeline.py[m
[1m+++ b/src/disaster_pulse_etl/pipeline.py[m
[36m@@ -1,7 +1,427 @@[m
[31m-from disaster_pulse_etl.utils.logger import [m
[31m-from disaster_pulse_etl.extraction.usgs import extract_earthquakes[m
[32m+[m[32mimport os[m
[32m+[m[32mfrom pathlib import Path[m
[32m+[m
[32m+[m[32mfrom disaster_pulse_etl.utils.logger import get_logger[m
[32m+[m
[32m+[m[32mfrom disaster_pulse_etl.utils.csv_storage import save_processed_csv[m
 from disaster_pulse_etl.utils.raw_storage import save_raw_json[m
[32m+[m[32mfrom disaster_pulse_etl.loading.s3 import upload_to_s3[m
[32m+[m
[32m+[m[32mfrom disaster_pulse_etl.extraction.usgs import extract_earthquakes[m
 from disaster_pulse_etl.transformation.earthquakes import transform_earthquakes[m
 from disaster_pulse_etl.validation.earthquake_validation import validate_earthquakes[m
[31m-from disaster_pulse_etl.utils.csv_storage import save_processed_csv[m
[31m-from disaster_pulse_etl.loading.s3 import upload_to_s3[m
\ No newline at end of file[m
[32m+[m
[32m+[m
[32m+[m[32mfrom disaster_pulse_etl.extraction.eonet import extract_eonet[m
[32m+[m[32mfrom disaster_pulse_etl.transformation.eonet_events import transform_eonet[m
[32m+[m[32mfrom disaster_pulse_etl.validation.eonet_validation import validate_eonet[m
[32m+[m
[32m+[m
[32m+[m[32mUSGS_SOURCE = "USGS"[m
[32m+[m[32mUSGS_DATASET = "earthquakes"[m
[32m+[m
[32m+[m[32mEONET_SOURCE = "NASA"[m
[32m+[m[32mEONET_DATASET = "eonet"[m
[32m+[m
[32m+[m[32mPROCESSED_BASE_PATH = Path("data/processed")[m
[32m+[m
[32m+[m[32mS3_BUCKET = "disaster-pulse-etl-ak26"[m
[32m+[m[32mS3_PREFIX = "disaster-pulse"[m
[32m+[m
[32m+[m
[32m+[m[32mlogger = get_logger()[m
[32m+[m
[32m+[m
[32m+[m[32mdef run_usgs_pipeline([m
[32m+[m[32m    bucket: str[m
[32m+[m[32m) -> dict[str, str] | None:[m
[32m+[m[32m    """[m
[32m+[m[32m    Run the USGS earthquake ETL pipeline.[m
[32m+[m
[32m+[m[32m    Parameters[m
[32m+[m[32m    ----------[m
[32m+[m[32m    bucket: str -> Destination S3 bucket name.[m
[32m+[m
[32m+[m[32m    Returns[m
[32m+[m[32m    -------[m
[32m+[m[32m    dict[str, str] | None -> Dictionary containing output artifact paths[m
[32m+[m[32m        when successful. Returns None when validation fails.[m
[32m+[m[32m    """[m
[32m+[m
[32m+[m[32m    logger.info("Starting DisasterPulse USGS ETL pipeline")[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m
[32m+[m[32m        logger.info("Starting USGS earthquake data extraction")[m
[32m+[m
[32m+[m[32m        data = extract_earthquakes()[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "USGS earthquake data extraction completed"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info("Saving raw USGS response")[m
[32m+[m
[32m+[m[32m        raw_path = save_raw_json([m
[32m+[m[32m            data=data,[m
[32m+[m[32m            source=USGS_SOURCE,[m
[32m+[m[32m            dataset=USGS_DATASET[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Raw USGS response saved: %s",[m
[32m+[m[32m            raw_path[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Starting USGS earthquake transformation"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        df = transform_earthquakes(data)[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "USGS earthquake transformation completed: "[m
[32m+[m[32m            "%s records",[m
[32m+[m[32m            len(df)[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Starting USGS earthquake data validation"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        validation_result = validate_earthquakes(df)[m
[32m+[m
[32m+[m[32m        for warning in validation_result["warnings"]:[m
[32m+[m[32m            logger.warning(warning)[m
[32m+[m
[32m+[m[32m        for error in validation_result["errors"]:[m
[32m+[m[32m            logger.error(error)[m
[32m+[m
[32m+[m[32m        if validation_result["status"] == "FAILED":[m
[32m+[m[32m            logger.error([m
[32m+[m[32m                "USGS earthquake validation failed. "[m
[32m+[m[32m                "Pipeline execution stopped."[m
[32m+[m[32m            )[m
[32m+[m[32m            return None[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "USGS earthquake validation passed. "[m
[32m+[m[32m            "Continuing pipeline."[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Saving processed USGS earthquake data"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        processed_path = save_processed_csv([m
[32m+[m[32m            df=df,[m
[32m+[m[32m            source=USGS_SOURCE,[m
[32m+[m[32m            dataset=USGS_DATASET[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Processed USGS earthquake data saved: %s",[m
[32m+[m[32m            processed_path[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        relative_processed_path = ([m
[32m+[m[32m            processed_path[m
[32m+[m[32m            .relative_to(PROCESSED_BASE_PATH.parent)[m
[32m+[m[32m            .as_posix()[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        s3_key = ([m
[32m+[m[32m            f"{S3_PREFIX}/{relative_processed_path}"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Uploading processed USGS data to S3: "[m
[32m+[m[32m            "s3://%s/%s",[m
[32m+[m[32m            bucket,[m
[32m+[m[32m            s3_key[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        s3_uri = upload_to_s3([m
[32m+[m[32m            local_file=processed_path,[m
[32m+[m[32m            bucket=bucket,[m
[32m+[m[32m            s3_key=s3_key[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Processed USGS data uploaded: %s",[m
[32m+[m[32m            s3_uri[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "DisasterPulse USGS ETL pipeline "[m
[32m+[m[32m            "completed successfully"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        return {[m
[32m+[m[32m            "raw_path": str(raw_path),[m
[32m+[m[32m            "processed_path": str(processed_path),[m
[32m+[m[32m            "s3_uri": s3_uri[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m    except Exception:[m
[32m+[m[32m        logger.exception([m
[32m+[m[32m            "DisasterPulse USGS ETL pipeline failed"[m
[32m+[m[32m        )[m
[32m+[m[32m        raise[m
[32m+[m
[32m+[m[32mdef run_eonet_pipeline([m
[32m+[m[32m    bucket: str,[m
[32m+[m[32m) -> dict[str, object] | None:[m
[32m+[m[32m    """[m
[32m+[m[32m    Run the NASA EONET ETL pipeline.[m
[32m+[m
[32m+[m[32m    Parameters[m
[32m+[m[32m    ----------[m
[32m+[m[32m    bucket : str[m
[32m+[m[32m        Destination S3 bucket name.[m
[32m+[m
[32m+[m[32m    Returns[m
[32m+[m[32m    -------[m
[32m+[m[32m    dict[str, object] | None[m
[32m+[m[32m        Dictionary containing output artifact paths[m
[32m+[m[32m        when successful.[m
[32m+[m
[32m+[m[32m        Returns None when validation fails.[m
[32m+[m[32m    """[m
[32m+[m
[32m+[m[32m    logger.info([m
[32m+[m[32m        "Starting DisasterPulse NASA EONET ETL pipeline"[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Starting NASA EONET data extraction"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        data = extract_eonet()[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "NASA EONET data extraction completed"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Saving raw NASA EONET response"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        raw_path = save_raw_json([m
[32m+[m[32m            data=data,[m
[32m+[m[32m            source=EONET_SOURCE,[m
[32m+[m[32m            dataset=EONET_DATASET[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Raw NASA EONET response saved: %s",[m
[32m+[m[32m            raw_path[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Starting NASA EONET transformation"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        event_df, geometry_df = transform_eonet(data)[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "NASA EONET transformation completed: "[m
[32m+[m[32m            "events=%s, geometry=%s records",[m
[32m+[m[32m            len(event_df),[m
[32m+[m[32m            len(geometry_df)[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Starting NASA EONET data validation"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        validation_result = validate_eonet([m
[32m+[m[32m            event_df,[m
[32m+[m[32m            geometry_df[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        for warning in validation_result["warnings"]:[m
[32m+[m[32m            logger.warning(warning)[m
[32m+[m
[32m+[m[32m        for error in validation_result["errors"]:[m
[32m+[m[32m            logger.error(error)[m
[32m+[m
[32m+[m[32m        if validation_result["status"] == "FAILED":[m
[32m+[m[32m            logger.error([m
[32m+[m[32m                "NASA EONET validation failed. "[m
[32m+[m[32m                "Pipeline execution stopped."[m
[32m+[m[32m            )[m
[32m+[m[32m            return None[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "NASA EONET validation passed. "[m
[32m+[m[32m            "Continuing pipeline."[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Saving processed NASA EONET event data"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        processed_path_event = save_processed_csv([m
[32m+[m[32m            df=event_df,[m
[32m+[m[32m            source=EONET_SOURCE,[m
[32m+[m[32m            dataset="event"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Processed NASA EONET event data saved: %s",[m
[32m+[m[32m            processed_path_event[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Saving processed NASA EONET geometry data"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        processed_path_geometry = save_processed_csv([m
[32m+[m[32m            df=geometry_df,[m
[32m+[m[32m            source=EONET_SOURCE,[m
[32m+[m[32m            dataset="geometry"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Processed NASA EONET geometry data saved: %s",[m
[32m+[m[32m            processed_path_geometry[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        relative_event_path = ([m
[32m+[m[32m            processed_path_event[m
[32m+[m[32m            .relative_to(PROCESSED_BASE_PATH.parent)[m
[32m+[m[32m            .as_posix()[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        s3_key_event = ([m
[32m+[m[32m            f"{S3_PREFIX}/{relative_event_path}"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Uploading processed NASA EONET event data "[m
[32m+[m[32m            "to S3: s3://%s/%s",[m
[32m+[m[32m            bucket,[m
[32m+[m[32m            s3_key_event[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        s3_uri_event = upload_to_s3([m
[32m+[m[32m            local_file=processed_path_event,[m
[32m+[m[32m            bucket=bucket,[m
[32m+[m[32m            s3_key=s3_key_event[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Processed NASA EONET event data uploaded: %s",[m
[32m+[m[32m            s3_uri_event[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        relative_geometry_path = ([m
[32m+[m[32m            processed_path_geometry[m
[32m+[m[32m            .relative_to(PROCESSED_BASE_PATH.parent)[m
[32m+[m[32m            .as_posix()[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        s3_key_geometry = ([m
[32m+[m[32m            f"{S3_PREFIX}/{relative_geometry_path}"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Uploading processed NASA EONET geometry data "[m
[32m+[m[32m            "to S3: s3://%s/%s",[m
[32m+[m[32m            bucket,[m
[32m+[m[32m            s3_key_geometry[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        s3_uri_geometry = upload_to_s3([m
[32m+[m[32m            local_file=processed_path_geometry,[m
[32m+[m[32m            bucket=bucket,[m
[32m+[m[32m            s3_key=s3_key_geometry[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "Processed NASA EONET geometry data uploaded: %s",[m
[32m+[m[32m            s3_uri_geometry[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "DisasterPulse NASA EONET ETL pipeline "[m
[32m+[m[32m            "completed successfully"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        return {[m
[32m+[m[32m            "raw_path": str(raw_path),[m
[32m+[m[32m            "processed_path": [[m
[32m+[m[32m                str(processed_path_event),[m
[32m+[m[32m                str(processed_path_geometry)[m
[32m+[m[32m            ],[m
[32m+[m[32m            "s3_uri": [[m
[32m+[m[32m                s3_uri_event,[m
[32m+[m[32m                s3_uri_geometry[m
[32m+[m[32m            ][m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m    except Exception:[m
[32m+[m[32m        logger.exception([m
[32m+[m[32m            "DisasterPulse NASA EONET ETL pipeline failed"[m
[32m+[m[32m        )[m
[32m+[m[32m        raise[m
[32m+[m
[32m+[m
[32m+[m[32mdef main() -> None:[m
[32m+[m[32m    """[m
[32m+[m[32m    Run all DisasterPulse ETL pipelines.[m
[32m+[m
[32m+[m[32m    The S3 bucket is taken from the S3_BUCKET environment[m
[32m+[m[32m    variable. A project-level default is currently used for[m
[32m+[m[32m    local development/testing.[m
[32m+[m[32m    """[m
[32m+[m
[32m+[m[32m    bucket = S3_BUCKET[m
[32m+[m
[32m+[m[32m    if not bucket:[m
[32m+[m[32m        raise ValueError([m
[32m+[m[32m            "S3_BUCKET is not set. "[m
[32m+[m[32m            "Set it before running the pipeline."[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    logger.info([m
[32m+[m[32m        "Starting DisasterPulse ETL orchestration"[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    usgs_result = run_usgs_pipeline([m
[32m+[m[32m        bucket=bucket[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    if usgs_result is None:[m
[32m+[m[32m        logger.error([m
[32m+[m[32m            "USGS pipeline completed with validation failure."[m
[32m+[m[32m        )[m
[32m+[m[32m    else:[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "USGS pipeline completed successfully."[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    eonet_result = run_eonet_pipeline([m
[32m+[m[32m        bucket=bucket[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    if eonet_result is None:[m
[32m+[m[32m        logger.error([m
[32m+[m[32m            "NASA EONET pipeline completed with "[m
[32m+[m[32m            "validation failure."[m
[32m+[m[32m        )[m
[32m+[m[32m    else:[m
[32m+[m[32m        logger.info([m
[32m+[m[32m            "NASA EONET pipeline completed successfully."[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    logger.info([m
[32m+[m[32m        "DisasterPulse ETL orchestration completed"[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m
[32m+[m[32mif __name__ == "__main__":[m
[32m+[m[32m    main()[m
\ No newline at end of file[m
[1mdiff --git a/src/disaster_pulse_etl/utils/logger.py b/src/disaster_pulse_etl/utils/logger.py[m
[1mindex e69de29..85b3a94 100644[m
[1m--- a/src/disaster_pulse_etl/utils/logger.py[m
[1m+++ b/src/disaster_pulse_etl/utils/logger.py[m
[36m@@ -0,0 +1,38 @@[m
[32m+[m[32mimport logging[m
[32m+[m[32mfrom pathlib import Path[m
[32m+[m
[32m+[m[32mdef get_logger(name: str = "disaster_pulse") -> logging.Logger:[m
[32m+[m[32m    """[m
[32m+[m[32m    Create and return the application logger.[m
[32m+[m[32m    """[m
[32m+[m
[32m+[m[32m    logger = logging.getLogger(name)[m
[32m+[m
[32m+[m[32m    if logger.handlers:[m
[32m+[m[32m        return logger[m
[32m+[m
[32m+[m[32m    logger.setLevel(logging.INFO)[m
[32m+[m
[32m+[m[32m    log_directory = Path("logs")[m
[32m+[m[32m    log_directory.mkdir(exist_ok=True)[m
[32m+[m
[32m+[m[32m    log_file = log_directory / "etl.log"[m
[32m+[m
[32m+[m[32m    formatter = logging.Formatter([m
[32m+[m[32m        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    file_handler = logging.FileHandler([m
[32m+[m[32m        log_file,[m
[32m+[m[32m        encoding="utf-8"[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    console_handler = logging.StreamHandler()[m
[32m+[m
[32m+[m[32m    file_handler.setFormatter(formatter)[m
[32m+[m[32m    console_handler.setFormatter(formatter)[m
[32m+[m
[32m+[m[32m    logger.addHandler(file_handler)[m
[32m+[m[32m    logger.addHandler(console_handler)[m
[32m+[m
[32m+[m[32m    return logger[m
