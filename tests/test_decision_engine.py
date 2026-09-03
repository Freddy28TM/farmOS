from backend.app.decision_engine import assess_water_risk


def test_low_water_risk():
    result = assess_water_risk(
        recent_rainfall=30,
        forecast_rainfall=30,
        temperature=24,
        crop="maize",
        growth_stage="vegetative",
    )

    assert result["risk_level"] == "LOW"
    assert result["context"] == "Crop: maize, Growth stage: vegetative"


def test_high_water_risk():
    result = assess_water_risk(
        recent_rainfall=2,
        forecast_rainfall=2,
        temperature=35,
        crop="maize",
        growth_stage="vegetative",
    )

    assert result["risk_level"] == "HIGH"
    assert result["context"] == "Crop: maize, Growth stage: vegetative"
