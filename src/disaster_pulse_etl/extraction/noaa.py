
import os
import requests
from dotenv import load_dotenv
from pathlib import Path


NOAA_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"

NOAA_ENDPOINTs = ["data","stations","datatypes"]


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

    while True:
        
        request_params = {
            **params,
            "limit":limit,
            "offset":offset
        }

        response = requests.get(
            url,
            headers=headers,
            params=request_params,
            timeout=timeout
        )

        response.raise_for_status()

        page = response.json()

        results = page.get("results",[])

        if not results:
            break

        all_results.extend(results)

        resultset = (
            page.get("metadata",{})
            .get("resultset", {})
        )

        total_count = resultset.get("count")

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
    
def extract_noaa_data() -> dict:
    """
    Extract global GHCND observations.
    """
    
    params = {
        "datasetid": "GHCND",
        "startdate": "2026-09-01",
        "enddate": "2026-09-01",
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

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

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

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()