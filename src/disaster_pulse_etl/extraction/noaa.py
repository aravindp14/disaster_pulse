
import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta, timezone

from disaster_pulse_etl.utils.logger import get_logger
from disaster_pulse_etl.utils.http_client import get_with_retry

logger = get_logger()


# start_date = (today - timedelta(days=10)).isoformat()
# end_date = (today - timedelta(days=5)).isoformat()

# start_date = (today - timedelta(days=3)).isoformat()

# end_date = (today - timedelta(days=1)).isoformat()

NOAA_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"

NOAA_ENDPOINTs = ["data","stations","datatypes"]


class NOAANoDataError(Exception):
    """Custom exception for NOAA API no data response."""
    pass

def extract_noaa(endpoint: str,
    params: dict | None = None,
    timeout: int = 30
) -> dict:
    """
    Extract paginated data from a NOAA API endpoint.

    Parameters
    ------------
    endpoint : str
        NOAA API endpoint, e.g. "data", "stations",
        or "datatypes".

    params : dict | None
        Query parameters for the NOAA API.

    Returns
    ------------
    dict
        Complete NOAA API response containing all pages.
    """

    
    env_path= Path(
        r"D:\repository\disaster_pulse\disaster_pulse_etl"
        r"\src\disaster_pulse_etl\.env"
    )
    
    load_dotenv(env_path)
    
    token = os.getenv("NOAA_TOKEN")
    
    if not token:
        raise ValueError("NOAA_TOKEN is not set.")

    url = f"{NOAA_URL}/{endpoint}"

    headers = {"token": token}

    params = params.copy() if params else {}

    limit = 1000
    offset = 1

    all_results = []
    total_count = 0

    while True:
        
        request_params = {
            **params,
            "limit":limit,
            "offset":offset
        }

        response = get_with_retry(
            url,
            headers=headers,
            params=request_params,
            timeout=timeout
        )

        # print("Requested URL:", response.url)
        # print("Response:", page)

        response.raise_for_status()

        logger.info(
            "NOAA response: Status = %s, URL = %s, body = %s",
            response.status_code,
            response.url,
            response.text[:300]
        )

        page = response.json()

        if not isinstance(page, dict):
            raise ValueError(f"NOAA returned an unexpected JSON response: {response.url}")

        if not page or not page.get("results"):
            if endpoint == "data" and offset == 1:
                raise NOAANoDataError(
                    f"NOAA returned no observations for"
                    f" {params.get('startdate')} to {params.get('enddate')}: {response.url}"
                )

            raise ValueError(f"Unexpected empty NOAA page at offset {offset}: {response.url}")
        
            

        results = page.get("results",[])

        resultset = (
                    page.get("metadata",{})
                    .get("resultset", {})
                )

        total_count = resultset.get("count")

        if not results:
            break        

        all_results.extend(results)

        if total_count is None:
            break

        if len(all_results) >= total_count:
            break

        offset += limit

    return{
        "metadata": {
            "resultset": {
                "count": total_count,
                "limit": limit
            }
    },
    "results": all_results
    }
    
def extract_noaa_data(observation_date: str | None = None) -> dict:
    """
    Extract global GHCND observations.
    """

    if observation_date is None:
        today = datetime.now(timezone.utc).date()
        observation_date = (today - timedelta(days=5)).isoformat()
    
    params = {
        "datasetid": "GHCND",
        "startdate": observation_date,
        "enddate": observation_date,
        "units": "metric",
    }
    
    return extract_noaa(
        endpoint="data",
        params=params,
    )

def extract_noaa_stations() -> dict:
    """
    Extract NOAA station metadata.
    """

    params = {
        "datasetid": "GHCND",
    }

    return extract_noaa(
        endpoint="stations",
        params=params,
        timeout=120
    )

def extract_noaa_datatypes() -> dict:
    """
    Extract NOAA datatype metadata.
    """
    
    params = {
        "datasetid": "GHCND",
    }
    
    return extract_noaa(
        endpoint="datatypes",
        params=params,
    )

def extract_noaa_station(station_id: str) -> dict:
    """
    Extract metadata for a single NOAA station
    """
    env_path= Path(
        r"D:\repository\disaster_pulse\disaster_pulse_etl"
        r"\src\disaster_pulse_etl\.env"
    )

    load_dotenv(env_path)

    token = os.getenv("NOAA_TOKEN")

    if not token:
        raise ValueError("NOAA_TOKEN is not set")

    url = f"{NOAA_URL}/stations/{station_id}"

    headers={
        "token":token
    }

    response = get_with_retry(
        url,
        headers=headers,
        timeout=30
    )


    return response.json()

def extract_noaa_datatype(
        datatype_id:str
) -> dict:
    """
    Extact metadata for a single NOAA datatype
    """

    env_path = Path(
        f"D:\repository\disaster_pulse\disaster_pulse_etl"
        f"\src\disaster_pulse_etl\.env"
    )

    load_dotenv(env_path)

    token = os.getenv("NOAA_TOKEN")

    if not token:
        raise ValueError("NOAA_TOKEN is not set")

    url = f"{NOAA_URL}/datatypes/{datatype_id}"

    headers = {
        "token": token
    }

    response = get_with_retry(
        url,
        headers=headers,
        timeout=30
    )


    return response.json()