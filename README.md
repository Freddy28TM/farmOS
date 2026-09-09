# FarmOS

## Explainable environmental risk intelligence for small-scale farmers

FarmOS is a modular agricultural decision-support system designed to help small-scale farmers interpret environmental conditions and make more informed decisions.

The current MVP focuses on **water-stress risk for maize**. FarmOS combines farm context, environmental data, a transparent deterministic decision engine, persistent risk assessments, explanations, recommendations, and farmer feedback into one workflow.

> **Agricultural decision support should be understandable, traceable, and useful to the farmer.**

---

## The Problem

Small-scale farmers often make decisions under changing and uncertain environmental conditions.

Rainfall may be limited or unpredictable. Temperatures may become unusually high. Weather information can describe what is happening without explaining what those conditions mean for a particular farm.

FarmOS addresses the decision-support gap between:

```text
Environmental information
          +
Farm context
          ↓
    Risk assessment
          ↓
    Explanation
          ↓
    Recommendation
          ↓
     Farmer action
          ↓
    Observed result
```

The goal is not simply to display environmental data or produce an unexplained prediction.

FarmOS provides a **traceable decision-support result** that allows the farmer to understand why a risk level was produced.

---

## MVP Scope

The current MVP addresses one focused agricultural problem:

```text
Crop
Maize

Risk
Water stress
```

The assessment considers:

* Recent rainfall
* Forecast rainfall
* Temperature
* Farm location
* Crop
* Growth stage

The system produces:

* Risk level
* Risk score
* Confidence level
* Contributing factors
* Recommendation
* Human-readable explanation
* Assessment context
* Persistent assessment record

The farmer can subsequently record:

* Farmer action
* Observed result

This creates a feedback history without allowing feedback to automatically modify the decision engine.

---

## Current Capabilities

| Capability                    | Status      |
| ----------------------------- | ----------- |
| User registration             | Implemented |
| User login                    | Implemented |
| JWT authentication            | Implemented |
| Argon2 password hashing       | Implemented |
| Authenticated user profile    | Implemented |
| Farm creation                 | Implemented |
| Multiple farms per user       | Implemented |
| Farm ownership isolation      | Implemented |
| Environmental data retrieval  | Implemented |
| Environmental-data validation | Implemented |
| Maize water-stress assessment | Implemented |
| Growth-stage adjustment       | Implemented |
| Explainable risk factors      | Implemented |
| Persistent risk assessments   | Implemented |
| Assessment context storage    | Implemented |
| Farmer feedback persistence   | Implemented |
| API input validation          | Implemented |
| Automated backend testing     | Implemented |
| Static web frontend           | Implemented |

The MVP deliberately focuses on a clearly defined decision problem rather than attempting to model every agricultural risk.

---

# How FarmOS Works

The complete workflow is:

```text
Farmer
   │
   ▼
Web Frontend
   │
   ▼
Authentication
   │
   ▼
User-owned Farm
   │
   ▼
Environmental Data
   │
   ▼
Decision Engine
   │
   ▼
Risk Assessment
   │
   ├── Risk level
   ├── Score
   ├── Confidence
   ├── Factors
   ├── Recommendation
   └── Explanation
   │
   ▼
Persistent Assessment
   │
   ▼
Farmer Feedback
   │
   ├── Farmer action
   └── Observed result
```

The frontend does **not** contain the agricultural decision logic.

The backend coordinates authentication, authorization, farm access, environmental data retrieval, decision processing, persistence, and feedback.

The decision engine remains responsible for producing the agricultural risk assessment.

---

# Decision Engine

FarmOS currently uses a **transparent deterministic scoring model**.

The same valid inputs produce predictable results, making the current MVP easy to inspect, test, and explain.

## Environmental Rules

| Condition             | Score |
| --------------------- | ----: |
| Recent rainfall < 5   |    +2 |
| Forecast rainfall < 5 |    +2 |
| Temperature >= 35     |    +2 |

## Growth-Stage Rules

Growth stage modifies severity when environmental water stress is already present.

| Maize growth stage | Additional score |
| ------------------ | ---------------: |
| Flowering          |               +2 |
| Germination        |               +1 |
| Vegetative         |               +1 |
| Maturity           |               +0 |

The flowering adjustment reflects the MVP assumption that water stress during this stage deserves greater attention.

## Risk Thresholds

```text
Score >= 4  → HIGH
Score >= 2  → MEDIUM
Score < 2   → LOW
```

## Confidence

The current deterministic model uses:

```text
Score >= 2  → MEDIUM
Score < 2   → LOW
```

Confidence is a category produced by the current model. It should not be interpreted as a guarantee that the predicted agricultural outcome will occur.

## Explainability

Each assessment records the factors that contributed to the result.

For example:

```text
Low recent rainfall
High temperature
Maize is in a water-sensitive flowering stage
```

These factors are used to construct a human-readable explanation.

This makes the assessment traceable instead of presenting the farmer with an unexplained risk label.

Detailed decision-engine documentation is available in:

`docs/decision-engine.md`

---

# System Architecture

FarmOS separates presentation, API coordination, data access, environmental information, decision logic, and persistence.

```text
┌─────────────────────────────────┐
│          Web Frontend           │
│        HTML / CSS / JS          │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│           FastAPI API           │
│ Authentication / Authorization  │
│ Validation / Application Logic  │
└───────────────┬─────────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌───────────────┐ ┌──────────────────┐
│   Database    │ │ Environmental    │
│               │ │ Data Provider    │
│ Users         │ └────────┬─────────┘
│ Farms         │          │
│ Assessments   │          │
│ Feedback      │          │
└───────┬───────┘          │
        │                   │
        └────────┬──────────┘
                 ▼
       ┌─────────────────────┐
       │    Decision Engine  │
       │                     │
       │ Deterministic Rules │
       │ Risk Calculation    │
       │ Explanation         │
       └──────────┬──────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │ Persisted Assessment│
       │ + Farmer Feedback   │
       └─────────────────────┘
```

The architecture is intentionally modular so that environmental providers, crops, agricultural models, and additional decision-support components can be introduced without redesigning the entire application.

See:

`docs/architecture.md`

---

# Data Model

## User

A user record contains:

* ID
* Email
* Password hash
* Creation timestamp

Passwords are never stored as plaintext.

## Farm

A farm record contains:

* ID
* Owner
* Name
* Latitude
* Longitude
* Crop
* Growth stage
* Creation timestamp

Each farm belongs to its authenticated owner.

## Risk Assessment

An assessment stores:

* Farm
* Recent rainfall
* Forecast rainfall
* Temperature
* Risk level
* Score
* Confidence
* Factors
* Recommendation
* Explanation
* Context
* Farmer action
* Observed result
* Feedback timestamp
* Creation timestamp

This means an assessment is a persistent record associated with the farm rather than only a temporary API response.

---

# Authentication and Security

FarmOS uses authenticated user accounts and ownership-based authorization.

## Registration

Users register with:

* Email
* Password

Passwords are protected using Argon2-based password hashing through `pwdlib`.

## Login

Successful authentication produces a JWT access token.

Protected API requests use:

```http
Authorization: Bearer <access_token>
```

## JWT Secret

The JWT signing secret is supplied through the environment variable:

```text
FARMOS_JWT_SECRET
```

The secret is not stored in source code.

Tokens also have a defined expiration period.

## Authorization and Data Isolation

Farm data is associated with its owning user.

Protected operations verify that the authenticated user owns the requested farm.

Risk assessments are protected through their relationship to the user's farm.

This prevents an authenticated user from accessing another user's farm data through the API.

---

# Environmental Data

FarmOS currently uses the configured weather-data provider to obtain environmental information.

The environmental-data layer separates provider responses from the decision engine by normalizing the information consumed by the risk model.

The system validates environmental responses before using them for assessment.

If environmental information cannot safely be used, the API returns an appropriate service error rather than generating an assessment from invalid data.

The current environmental integration uses **Open-Meteo**.

---

# Persistence and Feedback

FarmOS maintains a persistent relationship between environmental conditions, assessments, recommendations, and farmer observations.

```text
Environmental conditions
          ↓
     Risk assessment
          ↓
     Recommendation
          ↓
      Farmer action
          ↓
     Observed result
```

Feedback is stored for future evaluation and improvement.

The current MVP **does not automatically retrain or modify the decision engine from feedback**.

This separation keeps the current decision process deterministic and auditable.

---

# API

The primary API endpoints are:

| Method | Endpoint                                     | Purpose                            | Authentication |
| ------ | -------------------------------------------- | ---------------------------------- | -------------- |
| GET    | `/`                                          | API health/root response           | No             |
| POST   | `/register`                                  | Register a user                    | No             |
| POST   | `/login`                                     | Authenticate and obtain JWT        | No             |
| GET    | `/me`                                        | Retrieve authenticated user        | Yes            |
| POST   | `/farms`                                     | Create a user's farm               | Yes            |
| GET    | `/farms`                                     | List the user's farms              | Yes            |
| POST   | `/water-risk`                                | Generate and persist an assessment | Yes            |
| POST   | `/risk-assessments/{assessment_id}/feedback` | Record farmer feedback             | Yes            |

---

# Farm Creation

Example request:

```json
{
  "name": "Demo Farm",
  "latitude": -1.286389,
  "longitude": 36.817223,
  "crop": "maize",
  "growth_stage": "flowering"
}
```

The current MVP validates:

* Latitude range
* Longitude range
* Farm name length
* Supported crop
* Supported growth stage

---

# Water-Risk Assessment

The assessment endpoint operates on a persisted farm.

Example request:

```json
{
  "farm_id": 1
}
```

The backend:

1. Authenticates the user.
2. Verifies farm ownership.
3. Retrieves environmental data.
4. Validates the environmental data.
5. Calls the decision engine.
6. Creates a persistent risk-assessment record.
7. Returns the assessment.

Example response:

```json
{
  "assessment_id": 1,
  "risk_level": "HIGH",
  "score": 6,
  "confidence": "MEDIUM",
  "factors": [
    "Low recent rainfall",
    "High temperature",
    "Maize is in a water-sensitive flowering stage"
  ],
  "recommendation": "Monitor soil moisture closely and prioritize appropriate water-conservation measures during flowering.",
  "explanation": "Water-stress risk increased because of: Low recent rainfall, High temperature, Maize is in a water-sensitive flowering stage.",
  "context": "Location: (-1.286389, 36.817223); Crop: maize; Growth stage: flowering."
}
```

---

# Farmer Feedback

Feedback is submitted against a persisted assessment.

Example:

```json
{
  "farmer_action": "Monitored soil moisture and applied appropriate water-conservation measures.",
  "observed_result": "Soil moisture remained adequate during the following period."
}
```

Endpoint:

```text
POST /risk-assessments/{assessment_id}/feedback
```

The feedback is associated with the original assessment so that the assessment history remains traceable.

---

# Frontend

The current frontend is a lightweight static web application built with:

* HTML
* CSS
* Vanilla JavaScript

The workflow is:

```text
Register
   ↓
Login
   ↓
Load user's farms
   ↓
Create/select farm
   ↓
Request water-risk assessment
   ↓
Display result
   ↓
Submit feedback
```

The frontend communicates with the FastAPI backend.

It does not implement the agricultural scoring rules itself.

The current frontend does not require a Node.js build system.

For production deployment, authentication-token storage, HTTPS, deployment configuration, and other browser-security controls should be hardened according to the selected deployment architecture.

---

# Technology Stack

| Layer              | Technology                    |
| ------------------ | ----------------------------- |
| Language           | Python                        |
| API framework      | FastAPI                       |
| ORM                | SQLAlchemy                    |
| Database           | SQLite                        |
| Authentication     | JWT                           |
| Password hashing   | Argon2 through `pwdlib`       |
| Frontend           | HTML, CSS, Vanilla JavaScript |
| Environmental data | Open-Meteo                    |
| Application server | Uvicorn                       |
| Testing            | pytest                        |

---

# Repository Structure

```text
farmOS/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── decision_engine.py
│   │   ├── environmental_data.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── security.py
│   ├── requirements-dev.txt
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── docs/
│   ├── architecture.md
│   ├── decision-engine.md
│   ├── problem.md
│   ├── requirements.md
│   ├── privacy-policy.md
│   └── terms-and-conditions.md
│
├── tests/
│   ├── test_api.py
│   ├── test_current_user.py
│   ├── test_database.py
│   ├── test_decision_engine.py
│   ├── test_environmental_data.py
│   ├── test_farms.py
│   ├── test_login.py
│   ├── test_registration.py
│   └── test_security.py
│
├── .gitignore
├── pyproject.toml
└── README.md
```

---

# Running FarmOS Locally

## 1. Clone the repository

```bash
git clone <repository-url>
cd farmOS
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install development dependencies

For the complete development and test environment:

```bash
pip install -r backend/requirements-dev.txt
```

The development requirements include the runtime dependencies as well as the packages required to execute the automated test suite.

## 4. Configure the JWT secret

Linux/macOS:

```bash
export FARMOS_JWT_SECRET="replace-with-a-strong-development-secret"
```

Do not commit secrets to the repository.

## 5. Start the API

```bash
uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## 6. Start the frontend

Open another terminal from the project root:

```bash
python3 -m http.server 5500 --directory frontend
```

Then open:

```text
http://127.0.0.1:5500
```

---

# Testing

FarmOS uses pytest for automated testing.

Run the complete suite from the project root:

```bash
pytest -q
```

The test suite covers areas including:

```text
Decision rules
      ↓
Boundary conditions
      ↓
Input validation
      ↓
Environmental-data handling
      ↓
Authentication
      ↓
Authorization
      ↓
User/farm ownership
      ↓
Database persistence
      ↓
Risk-assessment persistence
      ↓
Feedback persistence
      ↓
API integration
```

The current verified test suite contains **76 passing tests**.

Expected clean result:

```text
76 passed
```

The development dependency configuration also pins the testing dependencies required for reproducible execution.

---

# Current Scope and Limitations

FarmOS is intentionally an MVP.

Current agricultural scope:

```text
Crop:
Maize

Risk:
Water stress
```

Supported growth stages:

```text
Germination
Vegetative
Flowering
Maturity
```

The current deterministic model does not directly model:

* Soil moisture
* Soil type
* Evapotranspiration
* Irrigation infrastructure
* Crop varieties
* Pests
* Diseases
* Flooding
* Full drought classification
* Long-term climate projections
* Satellite-derived crop conditions
* Large-scale local agricultural expert knowledge

Environmental information is also subject to uncertainty.

Therefore:

> **FarmOS is a decision-support tool, not a guarantee of agricultural outcomes.**

Recommendations should be considered alongside farmer knowledge, local conditions, and appropriate agricultural guidance.

---

# Responsible Use

FarmOS is designed to **support rather than replace farmer judgment**.

The current model is a deterministic MVP decision-support mechanism. It should be evaluated against appropriate agricultural datasets, field observations, and domain expertise before being relied upon for high-stakes agricultural decisions.

The system should not present its output as certainty.

---

# Privacy and Data Protection

FarmOS is designed around user-owned farm data.

The application can process information including:

* Account email
* Farm information
* Farm location
* Risk assessments
* Farmer feedback

Access to farm and assessment information is protected through authenticated ownership checks in the backend.

Detailed information about data handling is provided in:

`docs/privacy-policy.md`

The privacy documentation distinguishes current application behavior from potential future product capabilities.

---

# Terms and Conditions

The project's terms governing acceptable use, agricultural decision-support limitations, user responsibilities, intellectual property, third-party services, and other conditions are available in:

`docs/terms-and-conditions.md`

---

# Future Roadmap

The current MVP provides a foundation for broader agricultural decision support.

## Agricultural Intelligence

Potential future capabilities include:

* Additional crops
* Additional growth-stage models
* Drought-risk assessment
* Heat-stress assessment
* Flood-risk assessment
* Excess-rainfall assessment
* Planting-condition assessment
* More localized agricultural recommendations

## Environmental Data

Potential future sources include:

* Historical climate data
* Seasonal climate signals
* Soil measurements
* IoT sensors
* Satellite observations
* Additional weather providers

## Decision Intelligence

Potential future approaches include:

* Statistical forecasting
* More sophisticated agricultural models
* Machine-learning models
* AI-assisted interpretation

Any future AI component should remain explainable and should augment rather than obscure the decision-support process.

## Product Experience

Potential improvements include:

* Richer assessment-history views
* Improved dashboards
* Notifications
* Mobile interfaces
* Offline-first capabilities
* Broader farmer feedback workflows

These are future extensions and are **not represented as current MVP capabilities**.

---

# Documentation

The project documentation is organized as follows:

| Document                       | Purpose                                                                       |
| ------------------------------ | ----------------------------------------------------------------------------- |
| `docs/problem.md`              | Problem definition and project motivation                                     |
| `docs/requirements.md`         | Functional and system requirements                                            |
| `docs/architecture.md`         | System architecture, responsibilities, boundaries, persistence, and data flow |
| `docs/decision-engine.md`      | Decision-engine design, scoring rules, thresholds, and explainability         |
| `docs/privacy-policy.md`       | Privacy and data-protection policy                                            |
| `docs/terms-and-conditions.md` | Terms governing use of FarmOS                                                 |

---

# Design Philosophy

FarmOS follows a modular architecture so that individual components can evolve independently.

The current implementation separates:

```text
User Interface
      ↓
API
      ↓
Authentication / Authorization
      ↓
Data Layer
      ↓
Environmental Data
      ↓
Decision Engine
      ↓
Persistence
      ↓
Feedback
```

This separation allows future environmental providers, agricultural models, crops, and intelligence systems to be introduced without requiring the entire application to be redesigned.

The decision engine remains independent from the web interface and external environmental-data provider implementation.

---

# Project Status

FarmOS currently represents a **functional MVP** with:

* Authenticated users
* User-owned farms
* Farm ownership isolation
* Environmental-data integration
* Deterministic water-risk assessment
* Growth-stage-aware assessment
* Explainable risk factors
* Human-readable recommendations
* Persistent assessments
* Farmer feedback
* Automated backend testing
* Static web frontend
* Modular architecture

The project intentionally demonstrates a focused agricultural decision-support platform rather than a complete farm-management system.

---

# Conclusion

FarmOS turns environmental information and farm context into an explainable agricultural risk assessment.

Its central workflow is:

```text
Farm context
      +
Environmental conditions
      ↓
Risk assessment
      ↓
Explanation
      ↓
Recommendation
      ↓
Farmer action
      ↓
Observed result
```

The MVP demonstrates how environmental data, transparent decision rules, authentication, persistence, and farmer feedback can be combined into a modular decision-support system.

The emphasis is not simply on producing a prediction.

It is on producing a **traceable and understandable decision-support result that a farmer can evaluate and act upon.**
