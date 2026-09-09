# FarmOS

## Explainable environmental risk intelligence for small-scale farmers

FarmOS is a modular agricultural decision-support system designed to help small-scale farmers interpret environmental conditions and make more informed decisions.

The current hackathon release focuses on **water-stress risk for maize**. FarmOS combines farm context, environmental data, a transparent deterministic decision engine, persistent risk assessments, explanations, recommendations, and farmer feedback into one workflow.

> **Agricultural decision support should be understandable, traceable, and useful to the farmer.**

**Release status: Hackathon Release — Frozen**

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

## Hackathon Scope

The FarmOS hackathon release addresses one focused agricultural problem:

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

The release deliberately focuses on a clearly defined decision problem rather than attempting to model every agricultural risk.

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

FarmOS uses a **transparent deterministic scoring model**.

The same valid inputs produce predictable results, making the current release easy to inspect, test, and explain.

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

The flowering adjustment reflects the release assumption that water stress during this stage deserves greater attention.

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
│          FastAPI API            │
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
       │   Decision Engine   │
       │                     │
       │ Deterministic Rules │
       │ Risk Calculation     │
       │ Explanation          │
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

An assessment is therefore a persistent record associated with a farm rather than only a temporary API response.

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

The JWT signing secret is supplied through:

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

FarmOS currently uses **Open-Meteo** as its environmental-data provider.

The environmental-data layer separates provider responses from the decision engine by normalizing the information consumed by the risk model.

The system validates environmental responses before using them for assessment.

If environmental information cannot safely be used, the API returns an appropriate service error rather than generating an assessment from invalid data.

The environmental layer currently uses:

* Current temperature
* Recent precipitation
* Forecast precipitation
* Farm latitude and longitude

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

The current release **does not automatically retrain or modify the decision engine from feedback**.

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

The API validates:

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

The exact environmental values and resulting score depend on the live environmental conditions retrieved for the farm.

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

Feedback is associated with the assessment and its farm.

Ownership checks prevent users from submitting feedback against another user's assessment.

---

# Project Structure

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
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── docs/
│   ├── architecture.md
│   ├── decision-engine.md
│   ├── problem.md
│   ├── requirements.md
│   ├── privacy-policy.md
│   └── terms-and-conditions.md
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
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

Local runtime artifacts such as the SQLite database and Python virtual environments are intentionally excluded from version control.

---

# Running FarmOS Locally

## 1. Clone the repository

```bash
git clone https://github.com/Freddy28TM/farmOS.git
cd farmOS
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install application and development dependencies

For development and testing:

```bash
pip install -r backend/requirements-dev.txt
```

The development requirements include the application requirements and the pinned test dependencies.

## 4. Configure the JWT secret

Set a local environment variable before starting the API:

```bash
export FARMOS_JWT_SECRET="replace-with-a-strong-local-secret"
```

Do not commit secrets to the repository.

## 5. Start the API

From the repository root:

```bash
uvicorn backend.app.main:app --reload
```

The API is available locally at:

```text
http://127.0.0.1:8000
```

## 6. Run the frontend

The frontend is a static HTML/CSS/JavaScript application.

Serve the `frontend/` directory with a local static server, for example:

```bash
python3 -m http.server 5500 --directory frontend
```

Then open:

```text
http://127.0.0.1:5500
```

The frontend communicates with the locally running FastAPI backend.

---

# Testing

FarmOS includes automated backend tests covering:

* API behavior
* User authentication
* Current-user authorization
* Database behavior
* Decision-engine rules
* Environmental-data validation
* Farm ownership
* Login
* Registration
* Security and token handling
* Feedback persistence and ownership

The final hackathon release was verified with:

```text
76 passed
```

Run the complete test suite with:

```bash
pytest -q
```

A clean release should pass the complete suite before submission.

---

# Documentation

Additional technical and policy documentation is available in `docs/`:

| Document                  | Purpose                                            |
| ------------------------- | -------------------------------------------------- |
| `architecture.md`         | System architecture and component responsibilities |
| `decision-engine.md`      | Decision-engine rules and risk logic               |
| `problem.md`              | Problem definition and project motivation          |
| `requirements.md`         | Functional and non-functional requirements         |
| `privacy-policy.md`       | Privacy and data-handling policy                   |
| `terms-and-conditions.md` | Project terms and conditions                       |

---

# Design Principles

FarmOS is built around the following principles:

### Explainability

Risk results include contributing factors and human-readable explanations.

### Determinism

The current decision engine uses explicit rules rather than unexplained model output.

### Traceability

Environmental conditions, farm context, assessment results, and farmer feedback are persisted as related records.

### Data Isolation

Authenticated users can access only farms and assessments belonging to them.

### Testability

Core behavior is covered by an automated test suite.

### Modularity

Environmental data access, decision logic, API coordination, persistence, and frontend presentation are separated into distinct components.

---

# Hackathon Release Status

**FarmOS Hackathon Release — Frozen**

The hackathon implementation has been completed and regression-tested.

The release represents a focused MVP rather than a claim to solve every agricultural decision-support problem.

Future development may expand the system with additional crops, agricultural risks, environmental providers, analytics, deployment infrastructure, and other capabilities, but those are outside the frozen hackathon release.

---

# Limitations

The current release has deliberate limitations:

* The decision engine focuses on maize water-stress risk.
* The current scoring model is deterministic and rule-based.
* Environmental data depends on the configured external weather-data provider.
* The current persistence layer is designed for the hackathon/local deployment workflow.
* Farmer feedback is stored but does not automatically change the decision model.
* The static frontend currently communicates with the locally configured API.

These limitations are intentional boundaries of the hackathon MVP.

---

# Acknowledgements

FarmOS uses environmental information provided through the **Open-Meteo** weather API.

The project was developed for **NextStep Hacks 2026**.

---

# License

No open-source license is declared in this release unless one is explicitly included elsewhere in the repository.

All rights and reuse permissions should therefore be interpreted according to the repository owner's applicable terms and the accompanying Terms & Conditions.
