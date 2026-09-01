def assess_water_risk(
    recent_rainfall,
    forecast_rainfall,
    temperature,
):
    """
    Assess water-related agricultural risk.

    The MVP uses a simple deterministic scoring model.
    """

    score = 0
    factors = []

    if recent_rainfall < 5:
        score += 2
        factors.append("Low recent rainfall")

    if forecast_rainfall < 5:
        score += 2
        factors.append("Limited forecast rainfall")

    if temperature >= 35:
        score += 2
        factors.append("High temperature")

    if score >= 4:
        risk_level = "HIGH"
    elif score >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if score >= 4:
        confidence = "MEDIUM"
    elif score >= 2:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    if risk_level == "HIGH":
        recommendation = (
            "Monitor soil moisture and consider appropriate "
            "water-conservation measures."
        )
    elif risk_level == "MEDIUM":
        recommendation = (
            "Monitor soil moisture and weather conditions "
            "closely."
        )
    else:
        recommendation = (
            "Continue monitoring weather and farm conditions."
        )

    if factors:
        explanation = (
            "Water-stress risk increased because of: "
            + ", ".join(factors)
            + "."
        )
    else:
        explanation = (
            "Available conditions do not currently indicate "
            "significant water-stress risk."
        )

    return {
        "risk_level": risk_level,
        "score": score,
        "confidence": confidence,
        "factors": factors,
        "recommendation": recommendation,
        "explanation": explanation,
    }
