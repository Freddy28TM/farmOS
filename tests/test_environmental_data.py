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

def test_environmental_data_rejects_missing_temperature(monkeypatch):
    class InvalidResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def read(self):
            data = {
                "current": {},
                "hourly": {
                    "precipitation": [1] * 48,
                },
            }

            return json.dumps(data).encode()

    monkeypatch.setattr(
        "backend.app.environmental_data.urlopen",
        lambda url, timeout: InvalidResponse(),
    )

    try:
        get_environmental_data(
            latitude=-1.286389,
            longitude=36.817223,
        )
    except ValueError as error:
        assert "temperature" in str(error).lower()
    else:
        raise AssertionError(
            "Expected ValueError for missing temperature data"
        )

def test_environmental_data_rejects_missing_precipitation(monkeypatch):
    class InvalidResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def read(self):
            data = {
                "current": {
                    "temperature_2m": 24,
                },
                "hourly": {},
            }

            return json.dumps(data).encode()

    monkeypatch.setattr(
        "backend.app.environmental_data.urlopen",
        lambda url, timeout: InvalidResponse(),
    )

    try:
        get_environmental_data(
            latitude=-1.286389,
            longitude=36.817223,
        )
    except ValueError as error:
        assert "precipitation" in str(error).lower()
    else:
        raise AssertionError(
            "Expected ValueError for missing precipitation data"
        )

def test_environmental_data_rejects_insufficient_precipitation(
    monkeypatch,
):
    class InvalidResponse:
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
                    "precipitation": [1] * 24,
                },
            }

            return json.dumps(data).encode()

    monkeypatch.setattr(
        "backend.app.environmental_data.urlopen",
        lambda url, timeout: InvalidResponse(),
    )

    try:
        get_environmental_data(
            latitude=-1.286389,
            longitude=36.817223,
        )
    except ValueError as error:
        assert "48" in str(error)
    else:
        raise AssertionError(
            "Expected ValueError for insufficient precipitation data"
        )


def test_environmental_data_handles_network_failure(monkeypatch):
    def failing_urlopen(url, timeout):
        raise TimeoutError("Environmental data request timed out")

    monkeypatch.setattr(
        "backend.app.environmental_data.urlopen",
        failing_urlopen,
    )

    try:
        get_environmental_data(
            latitude=-1.286389,
            longitude=36.817223,
        )
    except ValueError as error:
        assert "request failed" in str(error).lower()
    else:
        raise AssertionError(
            "Expected ValueError for environmental data network failure"
        )
