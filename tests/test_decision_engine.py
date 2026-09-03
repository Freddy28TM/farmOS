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
    assert result["score"] == 0
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
    assert result["score"] == 7
    assert result["context"] == "Crop: maize, Growth stage: vegetative"


def test_vegetative_maize_gets_stage_adjustment():
    result = assess_water_risk(
        recent_rainfall=2,
        forecast_rainfall=30,
        temperature=24,
        crop="maize",
        growth_stage="vegetative",
    )

    assert result["score"] == 3
    assert result["risk_level"] == "MEDIUM"
    assert "Maize is in the vegetative stage" in result["factors"]


def test_flowering_maize_gets_stronger_stage_adjustment():
    result = assess_water_risk(
        recent_rainfall=2,
        forecast_rainfall=30,
        temperature=24,
        crop="maize",
        growth_stage="flowering",
    )

    assert result["score"] == 4
    assert result["risk_level"] == "HIGH"
    assert (
        "Maize is in a water-sensitive flowering stage"
        in result["factors"]
    )


def test_good_conditions_do_not_add_stage_bonus():
    result = assess_water_risk(
        recent_rainfall=30,
        forecast_rainfall=30,
        temperature=24,
        crop="maize",
        growth_stage="vegetative",
    )

    assert result["score"] == 0
    assert result["risk_level"] == "LOW"
    assert "Maize is in the vegetative stage" not in result["factors"]
