from backend.app.decision_engine import assess_water_risk


def test_low_water_risk():
    result = assess_water_risk(
        recent_rainfall=30,
        forecast_rainfall=30,
        temperature=24,
    )

    assert result["risk_level"] == "LOW"


def test_high_water_risk():
    result = assess_water_risk(
        recent_rainfall=2,
        forecast_rainfall=2,
        temperature=35,
    )

    assert result["risk_level"] == "HIGH"
