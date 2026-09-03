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

    with urlopen(url, timeout=10) as response:
        data = json.load(response)

    precipitation = data["hourly"]["precipitation"]

    recent_rainfall = sum(precipitation[:24])
    forecast_rainfall = sum(precipitation[24:48])

    return {
        "temperature": data["current"]["temperature_2m"],
        "recent_rainfall": recent_rainfall,
        "forecast_rainfall": forecast_rainfall,
    }
