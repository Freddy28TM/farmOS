# FarmOS

## Explainable environmental risk intelligence for small-scale farmers

FarmOS is a modular agricultural decision-support system that transforms environmental conditions into **clear, explainable, actionable risk assessments**.

The initial MVP focuses on one practical question:

> **Given current and near-term environmental conditions, what water-related risk should a maize farmer be aware of, and what should they consider doing next?**

FarmOS combines live environmental data, farm context, deterministic decision logic, and a simple web interface to turn weather information into a decision rather than simply displaying another forecast.

---

## The Problem

Small-scale farmers already have access to increasing amounts of weather information.

The harder problem is interpreting that information:

* What does the forecast mean for my farm?
* Is the current situation becoming risky?
* Which conditions are driving that risk?
* What should I monitor?
* How confident should I be in the assessment?

Climate variability makes this problem more important. Rainfall patterns can shift, temperatures can become extreme, and environmental conditions can change faster than farmers can comfortably interpret raw data.

**FarmOS addresses the gap between environmental information and practical agricultural decision-making.**

---

## Our Solution

FarmOS takes farm context and environmental information and converts them into an explainable assessment:

```text
Farm Context
     +
Environmental Data
     ↓
Decision Engine
     ↓
Risk Score
     ↓
LOW / MEDIUM / HIGH
     ↓
Risk Factors
     ↓
Recommendation
     ↓
Plain-language Explanation
```

The system deliberately avoids making unexplained AI predictions the foundation of the MVP.

Instead, the initial decision engine uses transparent, deterministic rules that can be inspected, tested, explained, and improved.

---

## MVP

The current MVP focuses on:

**Crop:** Maize

**Risk type:** Water stress

**Environmental signals:**

* Recent rainfall
* Forecast rainfall
* Temperature

**Farm context:**

* Location
* Crop
* Growth stage

**Risk levels:**

* LOW
* MEDIUM
* HIGH

**Output includes:**

* Risk level
* Risk score
* Confidence
* Contributing factors
* Recommendation
* Explanation
* Farm context

This intentionally narrow scope allows FarmOS to demonstrate a complete and testable decision-support foundation before expanding into additional crops and risk categories.

---

## Example

A farmer provides:

```text
Location: Nairobi, Kenya
Crop: Maize
Growth stage: Flowering
```

FarmOS retrieves environmental information and evaluates it using the decision engine.

For example, conditions involving:

```text
Low recent rainfall
+
High temperature
+
Maize flowering stage
```

can increase the calculated water-stress risk.

The result explains **why** the risk increased rather than presenting an unexplained prediction.

Example output:

```text
Risk: HIGH
Confidence: MEDIUM

Risk factors:
- Low recent rainfall
- High temperature
- Maize is in a water-sensitive flowering stage

Recommendation:
Monitor soil moisture closely and prioritize
appropriate water-conservation measures during flowering.

Explanation:
Water-stress risk increased because of the
identified environmental and farm-context factors.
```

---

## Key Features

### 🌦️ Environmental intelligence

FarmOS retrieves environmental information from the Open-Meteo weather API and extracts:

* Current temperature
* Recent precipitation
* Forecast precipitation

The environmental-data layer validates the returned values before passing them to the decision engine.

### 🧠 Explainable decision engine

The decision engine is implemented as a deterministic Python component independent of FastAPI.

This provides:

* Transparent rules
* Deterministic results
* Easy testing
* Clear contributing factors
* A replaceable decision layer

### 👨‍🌾 Farm management

Authenticated users can create and retrieve their farms.

Farm records include:

* Farm name
* Location
* Crop
* Growth stage

Farm ownership is associated with the authenticated user.

### 🔐 Authentication and security

FarmOS includes:

* User registration
* Password hashing
* JWT authentication
* Authenticated user identification
* User-owned farm records
* API input validation
* Coordinate validation
* Crop validation
* Growth-stage validation

Passwords are not stored as plaintext. Password hashing uses Argon2 through `pwdlib`.

JWT signing requires the `FARMOS_JWT_SECRET` environment variable.

### 📊 Explainable risk output

Each assessment can communicate:

```text
Risk Level
Score
Confidence
Factors
Recommendation
Explanation
Context
```

This makes the reasoning behind an assessment visible to the user.

### 🧪 Automated testing

FarmOS includes tests covering:

* Database behavior
* Farm creation and retrieval
* Current-user authentication
* Environmental-data validation
* Decision-engine behavior
* API behavior
* Registration
* Login
* Security
* Invalid inputs
* Authentication failures
* Environmental-data failures
* End-to-end risk-assessment behavior

The project is designed so that core decision logic can be tested independently from the web framework.

---

## Architecture

FarmOS separates the major system responsibilities:

```text
                     ┌──────────────────┐
                     │     Farmer       │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │    Frontend      │
                     │ HTML/CSS/JS      │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │   FastAPI API    │
                     └───────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       Authentication      Farm Data   Environmental Data
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌──────────────────┐
                    │ Decision Engine  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Risk Assessment  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Recommendation   │
                    │ + Explanation    │
                    └──────────────────┘
```

The architecture is intentionally modular so that additional environmental providers, crops, risk models, sensors, satellite data, or machine-learning components can be introduced without replacing the entire application.

---

## Technology Stack

| Layer              | Technology                      |
| ------------------ | ------------------------------- |
| Backend API        | FastAPI                         |
| Language           | Python                          |
| Database           | SQLite                          |
| ORM                | SQLAlchemy                      |
| Authentication     | JWT                             |
| Password hashing   | Argon2 via `pwdlib`             |
| Validation         | Pydantic                        |
| Frontend           | HTML / CSS / Vanilla JavaScript |
| Environmental data | Open-Meteo                      |
| Testing            | pytest                          |

---

## Project Structure

```text
farmOS/
├── backend/
│   ├── __init__.py
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── database.py
│       ├── decision_engine.py
│       ├── environmental_data.py
│       ├── main.py
│       ├── models.py
│       └── security.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
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
├── docs/
│   ├── architecture.md
│   ├── decision-engine.md
│   ├── problem.md
│   └── requirements.md
│
├── .gitignore
└── README.md
```

---

## API

The current backend exposes the following primary endpoints:

| Method | Endpoint      | Purpose                             |
| ------ | ------------- | ----------------------------------- |
| GET    | `/`           | API health/root response            |
| POST   | `/register`   | Register a user                     |
| POST   | `/login`      | Authenticate and obtain JWT         |
| GET    | `/me`         | Retrieve the authenticated user     |
| POST   | `/farms`      | Create an authenticated user's farm |
| GET    | `/farms`      | List the authenticated user's farms |
| POST   | `/water-risk` | Generate a water-risk assessment    |

### Water-risk request

```json
{
  "latitude": -1.286389,
  "longitude": 36.817223,
  "crop": "maize",
  "growth_stage": "flowering"
}
```

### Response

```json
{
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

## Running FarmOS Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd farmOS
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure the JWT secret

Linux/macOS:

```bash
export FARMOS_JWT_SECRET="replace-with-a-strong-development-secret"
```

Do not commit production secrets to the repository.

### 5. Start the API

```bash
uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the frontend

Serve the `frontend/` directory using a local HTTP server, for example:

```bash
python3 -m http.server 5500 --directory frontend
```

Then open:

```text
http://127.0.0.1:5500
```

---

## Testing

Run the automated test suite from the project root:

```bash
pytest
```

The tests are designed to verify both isolated components and API-level behavior.

Important test areas include:

```text
Decision rules
      ↓
Input validation
      ↓
Environmental-data failures
      ↓
Authentication
      ↓
Authorization
      ↓
Database behavior
      ↓
API integration
```

A clean test run is an important part of the FarmOS development and release process.

---

## Design Principles

FarmOS is built around six principles:

### 1. Correctness

The system should produce predictable results from defined inputs.

### 2. Explainability

Users should understand why an assessment was produced.

### 3. Simplicity

The MVP deliberately solves one agricultural decision problem rather than attempting to solve all farming problems simultaneously.

### 4. Testability

Core logic is separated from framework-specific code so it can be tested independently.

### 5. Security

Authentication, password protection, input validation, and user/farm ownership are considered part of the architecture.

### 6. Extensibility

The architecture is designed to support future crops, risk models, environmental data sources, sensors, satellite observations, and AI-assisted components.

---

## Current Scope and Limitations

FarmOS is an MVP and intentionally has a limited scope.

Current decision-support coverage focuses on:

```text
Crop: Maize
Risk: Water stress
```

The current frontend supports maize and four growth stages:

```text
Germination
Vegetative
Flowering
Maturity
```

The deterministic model is a decision-support mechanism, **not a guarantee of future agricultural outcomes**.

Weather information is inherently uncertain, and FarmOS should therefore be interpreted as an aid to decision-making rather than a replacement for farmer judgment or professional agricultural advice.

---

## Roadmap

The architecture allows FarmOS to expand toward:

### Agricultural expansion

* Additional crops
* Additional growth-stage models
* Drought risk
* Heat stress
* Flood risk
* Excess-rainfall risk
* Planting-condition assessment

### Data expansion

* Historical climate data
* Seasonal climate signals
* Soil measurements
* IoT sensors
* Satellite observations
* Additional weather providers

### Intelligence expansion

* More sophisticated agricultural models
* Statistical forecasting
* Machine-learning models
* AI-assisted interpretation

AI should augment the decision-support architecture rather than become an unexplained replacement for it.

### Product expansion

* Assessment history
* Farmer feedback
* Improved dashboards
* Notifications
* Mobile interfaces
* Multi-farm management
* More localized agricultural recommendations

---

## Documentation

Detailed project documentation is available in:

* `docs/problem.md` — problem definition and project goal
* `docs/requirements.md` — functional and architectural requirements
* `docs/architecture.md` — system architecture and data flow
* `docs/decision-engine.md` — decision-engine design and explainability principles

---

## Hackathon Focus

FarmOS is designed to demonstrate a practical principle:

> **Environmental data becomes more valuable when it can be translated into understandable decisions.**

Rather than building another weather dashboard, FarmOS focuses on the decision layer between raw environmental information and action.

The MVP demonstrates this principle through a focused, explainable water-risk workflow for maize farmers.

---

## Status

**Current stage: MVP / active development**

The core application includes:

* FastAPI backend
* SQLite persistence
* User registration
* JWT authentication
* Password hashing
* Farm ownership
* Environmental-data integration
* Deterministic water-risk decision engine
* Explainable risk results
* Vanilla JavaScript frontend
* Automated tests
* Technical documentation

The project is being hardened and polished toward a submission-ready release.

---

## License

Add the project's chosen license before public release.

---

## Acknowledgements

FarmOS uses environmental information provided through the Open-Meteo weather API.

The project is built as an open, modular experiment in explainable agricultural decision support.
