import json
import math
from urllib.parse import urlencode
from urllib.request import urlopen


def get_environmental_data(latitude, longitude):
    """
    Get environmental data for a farm location.

    Rainfall values are measured in millimetres (mm):
    - recent_rainfall: previous 24 hours
    - forecast_rainfall: next 24 hours

    Temperature is the current temperature in degrees Celsius.
    """

    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90"
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180"
        )

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

    if not isinstance(temperature, (int, float)):
        raise ValueError(
            "Environmental temperature must be numeric"
        )

    if not math.isfinite(temperature):
        raise ValueError(
            "Environmental temperature must be finite"
        )

    try:
        precipitation = data["hourly"]["precipitation"]
    except (KeyError, TypeError):
        raise ValueError(
            "Environmental data is missing precipitation"
        )

    if not isinstance(precipitation, list):
        raise ValueError(
            "Environmental precipitation must be a list"
        )

    if len(precipitation) < 48:
        raise ValueError(
            "Environmental data requires at least 48 "
            "precipitation values"
        )

    for value in precipitation[:48]:
        if not isinstance(value, (int, float)):
            raise ValueError(
                "Environmental precipitation values must be numeric"
            )

        if not math.isfinite(value):
            raise ValueError(
                "Environmental precipitation values must be finite"
            )

        if value < 0:
            raise ValueError(
                "Environmental precipitation values cannot be negative"
            )

    recent_rainfall = sum(precipitation[:24])
    forecast_rainfall = sum(precipitation[24:48])

    return {
        "temperature": temperature,
        "recent_rainfall": recent_rainfall,
        "forecast_rainfall": forecast_rainfall,
    }
