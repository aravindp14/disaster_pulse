import requests

world_bank_url = "https://api.worldbank.org/v2"

def extract_world_bank(
    indicator: str = "SP.POP.TOTL",
    country: str = "all",
    per_page: int = 1000
) -> dict:
    

    "Extract all pages for a World Bank indicator."

    url = f"{world_bank_url}/country/{country}/indicator/{indicator}"

    records = []
    page = 1
    total_pages = 1
    metadata = {}

    while page <= total_pages:
        response = requests.get(
            url,
            params={
                "format": "json",
                "per_page": per_page,
                "page": page
            },
            timeout=60
        )

        response.raise_for_status()
        payload = response.json()

        if (not isinstance(payload,list)) or (len(payload) < 2):
            raise ValueError("Unexpected World Bank API response.")

        metadata = payload[0] or {}
        records.extend(payload[1] or [])
        total_pages = metadata.get("pages", 1)

        page += 1

    return {
        "metadata": metadata,
        "records": records
    }