import requests

from disaster_pulse_etl.utils.raw_storage import save_raw_json

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

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()