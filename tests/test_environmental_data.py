import json

from backend.app.environmental_data import get_environmental_data


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def read(self):
        data = {
            "current": {
                "temperature_2m": 24,
            },
            "hourly": {
                "precipitation": [1] * 48,
            },
        }

        return json.dumps(data).encode()


def test_environmental_data_structure(monkeypatch):
    monkeypatch.setattr(
        "backend.app.environmental_data.urlopen",
        lambda url, timeout: FakeResponse(),
    )

    data = get_environmental_data(
        latitude=-1.286389,
        longitude=36.817223,
    )

    assert "temperature" in data
    assert "recent_rainfall" in data
    assert "forecast_rainfall" in data
