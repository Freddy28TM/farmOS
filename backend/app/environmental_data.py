from urllib.parse import urlencode
from urllib.request import urlopen
import json


def get_environmental_data(latitude, longitude):
    """
    Get environmental data for a farm location.

    Rainfall values are measured in millimetres (mm):
    - recent_rainfall: previous 24 hours
    - forecast_rainfall: next 24 hours

    Temperature is the current temperature in degrees Celsius.
    """

    params = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
            "hourly": "precipitation",
            "past_hours": 24,
            "forecast_hours": 24,
            "timezone": "UTC",
        }
    )

    url = "https://" + "api.open-meteo.com" + "/v1/forecast?" + params

    try:
        with urlopen(url, timeout=10) as response:
            data = json.load(response)
    except (TimeoutError, OSError) as error:
        raise ValueError(
            "Environmental data request failed"
        ) from error

    try:
        temperature = data["current"]["temperature_2m"]
    except (KeyError, TypeError):
        raise ValueError(
            "Environmental data is missing temperature"
        )

    try:
        precipitation = data["hourly"]["precipitation"]
    except (KeyError, TypeError):
        raise ValueError(
            "Environmental data is missing precipitation"
        )

    if len(precipitation) < 48:
        raise ValueError(
            "Environmental data requires at least 48 "
            "precipitation values"
        )

    recent_rainfall = sum(precipitation[:24])
    forecast_rainfall = sum(precipitation[24:48])

    return {
        "temperature": temperature,
        "recent_rainfall": recent_rainfall,
        "forecast_rainfall": forecast_rainfall,
    }
