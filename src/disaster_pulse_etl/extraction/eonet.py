

import requests

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


    response = requests.get(url,timeout=30)
    response.raise_for_status()
    return response.json()