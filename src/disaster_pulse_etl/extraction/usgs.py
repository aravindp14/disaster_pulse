import requests

from disaster_pulse_etl.utils.raw_storage import save_raw_json
from disaster_pulse_etl.utils.http_client import get_with_retry


USGS_EARTHQUAKE_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/"
    "summary/all_day.geojson"   
)

def extract_earthquakes(url: str = USGS_EARTHQUAKE_URL) -> dict:
    """
    Extract earthquake data from USGS GeoJSON API
    
    Parameters
    ------------
    url: str
    USGS earthquake feed URL.

    Returns
    ------------
    dict
    Raw JSON response from USGS.
    """

    response = get_with_retry(url, timeout=30)
    return response.json()