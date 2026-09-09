# FarmOS System Architecture

## 1. Architectural Goal

FarmOS is a modular agricultural decision-support system that transforms farm information and environmental conditions into explainable risk assessments and practical recommendations.

The current MVP focuses on one complete workflow:

```text
Farmer
  ↓
Frontend
  ↓
Authenticated API
  ↓
Farm Data
  ↓
Environmental Data
  ↓
Decision Engine
  ↓
Risk Assessment
  ↓
Recommendation + Explanation
  ↓
Persistent Assessment
  ↓
Farmer Feedback
```

The architecture separates:

* User interface
* API and application logic
* Authentication and authorization
* Farm data
* Environmental data
* Decision logic
* Persistent storage
* Feedback

This separation allows individual components to evolve without requiring the entire system to be redesigned.

---

## 2. Current System Architecture

The current FarmOS implementation consists of the following major layers:

```text
┌────────────────────────────────┐
│          FarmOS Frontend       │
│       HTML / CSS / JavaScript  │
└───────────────┬────────────────┘
                │ HTTP / JSON
                ▼
┌────────────────────────────────┐
│         FastAPI Backend        │
│                                │
│ Authentication                 │
│ Authorization                  │
│ Request Validation             │
│ Application Logic              │
│ API Endpoints                  │
└────────┬───────────────┬───────┘
         │               │
         │               ▼
         │      ┌──────────────────┐
         │      │ Environmental    │
         │      │ Data Layer       │
         │      │ Open-Meteo       │
         │      └────────┬─────────┘
         │               │
         ▼               ▼
┌────────────────────────────────┐
│         Decision Engine        │
│                                │
│ Environmental Rules            │
│ Crop Context                   │
│ Growth-Stage Adjustment        │
│ Risk Scoring                   │
│ Explainability                 │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│          Database              │
│                                │
│ Users                          │
│ Farms                          │
│ Risk Assessments               │
│ Feedback                       │
└────────────────────────────────┘
```

---

## 3. Frontend

The FarmOS frontend is a lightweight static web application implemented using:

* HTML
* CSS
* Vanilla JavaScript

The frontend communicates with the backend using HTTP requests and JSON responses.

### Responsibilities

The frontend is responsible for:

* User registration
* User login
* Maintaining the authenticated session
* Loading the user's farms
* Creating farms
* Selecting farms
* Requesting risk assessments
* Displaying risk levels
* Displaying risk scores
* Displaying confidence
* Displaying contributing factors
* Displaying recommendations
* Displaying explanations
* Submitting farmer feedback

The frontend does not contain the authoritative agricultural decision rules.

Keeping decision logic outside the frontend ensures that the core assessment behavior remains centralized, testable, and consistent.

---

## 4. Backend API

The backend is implemented using FastAPI.

It provides the main service boundary between the frontend and FarmOS internal components.

The backend is responsible for:

* Receiving HTTP requests
* Validating input
* Authenticating users
* Authorizing access to resources
* Managing farms
* Obtaining environmental data
* Calling the decision engine
* Persisting risk assessments
* Persisting feedback
* Returning structured JSON responses

The API separates transport concerns from decision logic and persistence.

---

## 5. Authentication and Authorization

FarmOS uses authenticated user accounts for protected resources.

The authentication flow is:

```text
Registration
    ↓
Password Hashing
    ↓
User Account
    ↓
Login
    ↓
JWT Access Token
    ↓
Authenticated API Request
```

Passwords are not stored as plaintext.

The backend uses password hashing and JWT-based authentication.

Authentication determines:

> Who is making the request?

Authorization determines:

> Is this user allowed to access the requested resource?

Farm ownership is enforced by the backend.

The authorization boundary can be represented as:

```text
Authenticated User
        ↓
Requested Resource
        ↓
Ownership Check
        ↓
Authorized / Rejected
```

This prevents a user from accessing another user's farm or related assessment data simply by supplying another resource identifier.

---

## 6. Farm Data

Farm data represents information belonging to an individual user's farm.

The current Farm model contains:

```text
Farm ID
Owner
Farm Name
Latitude
Longitude
Crop
Growth Stage
Creation Timestamp
```

Each farm is associated with its owner.

Farm location is used as environmental-data context, while crop and growth stage provide agricultural context for the decision engine.

Fields such as farm size and planting date are not required by the current implementation.

They may be introduced as future extensions if they become necessary for additional decision models.

---

## 7. Environmental Data

FarmOS currently obtains environmental information through an external weather-data provider.

The current provider is Open-Meteo.

The environmental-data layer is responsible for:

1. Receiving the farm's geographic location.
2. Requesting relevant environmental information.
3. Processing the provider response.
4. Validating environmental values.
5. Normalizing the data for the decision engine.

The architectural boundary is:

```text
Farm Location
      ↓
Environmental Provider
      ↓
Provider Response
      ↓
Validation / Normalization
      ↓
Decision Engine
```

The decision engine should operate on normalized environmental information rather than depending directly on provider-specific response formats.

This makes future replacement or addition of environmental providers easier.

---

## 8. Decision Engine

The decision engine is the core agricultural reasoning component of FarmOS.

Its purpose is to transform validated farm and environmental information into:

* Risk score
* Risk level
* Confidence
* Contributing factors
* Recommendation
* Explanation

The current MVP uses deterministic rules.

```text
Farm Context
     +
Environmental Conditions
     +
Agricultural Rules
     ↓
Risk Analysis
     ↓
Risk Score
     ↓
Risk Level
     ↓
Recommendation
     +
Explanation
```

The decision engine does not depend on an unexplained AI-generated response.

This provides:

* Reproducibility
* Explainability
* Testability
* Predictable behavior
* Easier debugging

AI and machine-learning techniques can be considered as future components, but they are not required for the current core decision process.

---

## 9. Current Risk Model

The MVP focuses on water-related risk.

Environmental conditions can increase the risk score when:

```text
Recent rainfall < 5
    → +2

Forecast rainfall < 5
    → +2

Temperature >= 35
    → +2
```

The decision engine also considers crop growth stage.

For the current maize-focused workflow:

```text
Flowering
    → +2

Germination
    → +1

Vegetative
    → +1

Maturity
    → +0
```

The resulting score determines the risk level:

```text
Score >= 4
    → HIGH

Score >= 2
    → MEDIUM

Score < 2
    → LOW
```

Confidence is currently represented as:

```text
Score >= 2
    → MEDIUM

Score < 2
    → LOW
```

The scoring rules are explicit and deterministic so that their behavior can be independently tested.

---

## 10. Explainability

FarmOS is designed so that an assessment can be traced through:

```text
INPUT
  ↓
TRIGGERED RULES
  ↓
RISK SCORE
  ↓
RISK LEVEL
  ↓
RECOMMENDATION
  ↓
EXPLANATION
```

For example, an assessment may identify factors such as:

```text
Low recent rainfall
High temperature
Maize is in a water-sensitive flowering stage
```

These factors are used to explain why the risk score increased.

The goal is not simply to return:

```text
HIGH
```

but to provide understandable information about the conditions that contributed to the result.

---

## 11. Persistence

FarmOS persists important application data in a relational database.

The current system stores information associated with:

* Users
* Farms
* Risk assessments
* Farmer feedback

The assessment workflow is:

```text
Assessment Request
       ↓
Environmental Data
       ↓
Decision Engine
       ↓
Assessment Result
       ↓
Database
       ↓
API Response
```

Persistence allows FarmOS to maintain assessment history rather than treating each assessment as a temporary calculation.

---

## 12. Risk Assessment Ownership

Risk assessments are associated with the farm and user context under which they were created.

The protected workflow is:

```text
Authenticated User
        ↓
Owned Farm
        ↓
Environmental Data
        ↓
Decision Engine
        ↓
Risk Assessment
        ↓
Persisted Record
```

The backend verifies ownership before allowing protected operations against user-owned resources.

This provides a clear data-isolation boundary between users.

---

## 13. Feedback Loop

FarmOS currently supports feedback associated with risk assessments.

The workflow is:

```text
Risk Assessment
      ↓
Recommendation
      ↓
Farmer Action
      ↓
Observed Result
      ↓
Feedback
      ↓
Persistent Record
```

The feedback record contains information about:

* Farmer action
* Observed result

Feedback currently provides an evaluation and historical record.

It does not automatically modify or retrain the decision engine.

This separation prevents unvalidated feedback from silently changing agricultural decision behavior.

Future versions may use accumulated feedback for system evaluation and improvement.

---

## 14. API Resource Boundaries

The current API is organized around several resource groups.

### Authentication

```text
POST /register
POST /login
GET  /me
```

### Farms

```text
POST /farms
GET  /farms
```

### Risk Assessment

```text
POST /water-risk
```

### Feedback

```text
POST /risk-assessments/{assessment_id}/feedback
```

Protected operations use authenticated user context and ownership checks where applicable.

---

## 15. Security Boundary

Security is enforced primarily at the API boundary.

```text
Internet
    ↓
Frontend
    ↓
FastAPI API
    ↓
Authentication
    ↓
Authorization
    ↓
Input Validation
    ↓
Application Logic
    ↓
Database
```

Current security controls include:

* Password hashing
* JWT authentication
* Protected API endpoints
* Ownership checks
* Request validation
* User/resource relationships
* Separation of authentication from decision logic

All client-provided input should be treated as untrusted.

The backend remains responsible for enforcing security decisions rather than relying on the frontend to enforce access restrictions.

---

## 16. Technology Independence

FarmOS is designed around component boundaries rather than direct dependence on a single technology.

For environmental data, the architecture is:

```text
Environmental Provider
        ↓
Environmental Data Layer
        ↓
Normalized Data
        ↓
Decision Engine
```

A future provider can use the same boundary:

```text
New Provider
      ↓
Environmental Data Layer
      ↓
Normalized Data
      ↓
Same Decision Engine
```

This approach reduces the amount of system code that must change when an external provider is replaced.

The same architectural principle can later be applied to:

* Additional weather providers
* Satellite services
* IoT sensors
* Soil-data systems
* Climate datasets
* Machine-learning models
* Alternative frontend applications

---

## 17. Current Architectural Limitations

The current architecture is intentionally scoped for the MVP.

Current limitations include:

* The primary implemented risk workflow is water-related risk.
* The current environmental provider is an external weather service.
* The decision rules are intentionally simple.
* The current database configuration is appropriate for the MVP and local development rather than large-scale production deployment.
* The frontend is a static application and requires additional production hardening before a public deployment.
* Feedback is persisted but does not automatically retrain or modify the decision engine.
* Advanced monitoring, auditing, rate limiting, and large-scale observability remain future production concerns.

These limitations are explicitly documented so that the scope of the current system is clear.

---

## 18. Architectural Principles

FarmOS prioritizes:

1. Correctness
2. Explainability
3. Simplicity
4. Testability
5. Security
6. Extensibility

The architecture is designed to demonstrate one complete decision-support workflow while maintaining clear boundaries between:

```text
User Interface
      ↓
API
      ↓
Authentication / Authorization
      ↓
Application Logic
      ↓
Environmental Data
      ↓
Decision Engine
      ↓
Persistence
      ↓
Feedback
```

The objective of the MVP is not to build the largest possible agricultural platform.

The objective is to establish a reliable, understandable, secure, and extensible foundation for future agricultural decision-support capabilities.
