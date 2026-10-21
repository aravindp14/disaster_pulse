import pandas as pd

def transform_population_data(
        data: dict
        ) -> pd.DataFrame:
    """
    Transform the population data DataFrame to match the desired schema.
    """
    # Example transformation: Rename columns, filter rows, etc.
    df = pd.json_normalize(data["records"])

    df = df[
        [
            "countryiso3code",
            "date",
            "value",
            "country.id",
            "country.value"
        ]
    ]


    df = df.rename(columns={
        "countryiso3code": "country_iso3_code",
        "date": "year",
        "value": "population",
        "country.id": "country_id",
        "country.value": "country_name"
    })
    
    # # Filter out rows with missing population data
    # df = df.dropna(subset=["population"])
    
    return df