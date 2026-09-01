# FarmOS Decision Engine

## Purpose

The decision engine converts farm and environmental information into an explainable agricultural risk assessment.

The first MVP will focus on identifying **water-related risk for maize**.

---

## Input

The initial decision engine will accept:

```text
Crop
Growth stage
Recent rainfall
Forecast rainfall
Temperature
```

---

## Processing

The engine evaluates the available inputs against documented agricultural rules.

The initial implementation will use deterministic rules rather than relying on an unexplained AI model.

Conceptually:

```text
Farm Data
    +
Weather Data
    ↓
Rules
    ↓
Risk Score
    ↓
Risk Level
    ↓
Recommendation
```

---

## Risk Levels

The MVP will use three risk levels:

```text
LOW
MEDIUM
HIGH
```

The risk level is derived from the conditions evaluated by the decision engine.

---

## Explainability

Every risk assessment should provide:

* Risk level
* Risk score or contributing factors
* Triggered conditions
* Recommendation
* Explanation
* Confidence or uncertainty where applicable

Example:

```text
Risk: MEDIUM

Contributing factors:
- Low recent rainfall
- Limited forecast rainfall

Recommendation:
Monitor soil moisture and consider appropriate
water-conservation measures.

Explanation:
The available rainfall information indicates
conditions that may increase water-stress risk.

Confidence:
MEDIUM
```

---

## Important Limitation

The decision engine does not claim to predict the future.

Weather and climate forecasts contain uncertainty.

FarmOS therefore presents its output as **decision support**, not guaranteed prediction.

---

## Future Expansion

The decision engine can later incorporate:

* Additional crops
* Crop-specific growth stages
* Soil information
* Historical climate data
* Seasonal climate signals
* Drought indicators
* Flood indicators
* Heat-stress indicators
* Satellite observations
* IoT sensor data
* Machine-learning models

These additions should extend the system without requiring the core architecture to be completely redesigned.
