import requests

from disaster_pulse_etl.utils.http_client import get_with_retry

EONET_URL = (
    "https://eonet.gsfc.nasa.gov/api/v3/events"
    "/geojson?status=all&days=7"
)

def extract_eonet(url: str = EONET_URL) -> dict:
    """
    Extract event data from NASA EONET API

    Parameters
    ------------
    url: str
    NASA EONET feed URL

    Returns
    ------------
    dict
    Raw JSON response from NASA EONET
    """


    response = get_with_retry(url, timeout=30)
    return response.json()