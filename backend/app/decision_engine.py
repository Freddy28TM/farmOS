def assess_water_risk(
    recent_rainfall,
    forecast_rainfall,
    temperature,
    crop,
    growth_stage,
):
    """
    Assess water-related agricultural risk.

    The MVP uses a simple deterministic scoring model.

    Environmental conditions establish whether water stress
    is present. Farm context can then increase the risk when
    the crop is in a water-sensitive growth stage.
    """

    score = 0
    factors = []

    context = f"Crop: {crop}, Growth stage: {growth_stage}"

    # Environmental risk factors
    if recent_rainfall < 5:
        score += 2
        factors.append("Low recent rainfall")

    if forecast_rainfall < 5:
        score += 2
        factors.append("Limited forecast rainfall")

    if temperature >= 35:
        score += 2
        factors.append("High temperature")

    # Determine whether environmental water stress exists.
    water_stress_present = (
        recent_rainfall < 5
        or forecast_rainfall < 5
        or temperature >= 35
    )

    # Farm-context adjustment
    # Growth stage affects severity only when water stress
    # is already present.
    if water_stress_present and crop.lower() == "maize":
        if growth_stage.lower() == "flowering":
            score += 2
            factors.append(
                "Maize is in a water-sensitive flowering stage"
            )

        elif growth_stage.lower() in ["germination", "vegetative"]:
            score += 1
            factors.append(
                f"Maize is in the {growth_stage.lower()} stage"
            )

    # Determine risk level
    if score >= 4:
        risk_level = "HIGH"
    elif score >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Determine confidence
    if score >= 4:
        confidence = "MEDIUM"
    elif score >= 2:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    # Generate recommendation
    if risk_level == "HIGH":
        if crop.lower() == "maize" and growth_stage.lower() == "flowering":
            recommendation = (
                "Monitor soil moisture closely and prioritize "
                "appropriate water-conservation measures during "
                "flowering."
            )
        else:
            recommendation = (
                "Monitor soil moisture and consider appropriate "
                "water-conservation measures."
            )

    elif risk_level == "MEDIUM":
        if temperature >= 35:
            recommendation = (
                "Monitor soil moisture and temperature "
                "conditions closely."
            )
        else:
            recommendation = (
                "Monitor soil moisture and weather conditions "
                "closely."
            )
    else:
        recommendation = (
            "Continue monitoring weather and farm conditions."
        )

    # Generate explanation
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
        "context": context,
    }
