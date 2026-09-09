# FarmOS Terms and Conditions

**Last Updated:** September 9, 2026

## 1. Introduction

These Terms and Conditions govern the use of FarmOS, an agricultural decision-support system designed to help users interpret environmental conditions and farm context.

By using FarmOS, users acknowledge that the system provides decision-support information and recommendations rather than guaranteed agricultural outcomes.

---

## 2. Description of FarmOS

FarmOS combines:

* Farm information
* Crop information
* Crop growth stage
* Environmental information
* Deterministic agricultural rules

to produce:

* Risk assessments
* Risk levels
* Confidence classifications
* Contributing factors
* Recommendations
* Explanations

The current MVP focuses primarily on water-related risk using maize as the main crop context.

---

## 3. Eligibility and Account Use

Where account registration is enabled, users are responsible for providing accurate information required to create and maintain their account.

Users are responsible for maintaining the confidentiality of their authentication credentials.

Users should not:

* Share their authentication credentials unnecessarily.
* Attempt to access another user's account.
* Attempt to bypass authentication or authorization controls.
* Use another person's account without authorization.

FarmOS may restrict access where necessary to protect the system, users, or application data.

---

## 4. Farm Information

Users may create farm records containing information such as:

* Farm name
* Location
* Crop
* Growth stage

Users are responsible for ensuring that information they provide is reasonably accurate for the intended use of the system.

FarmOS uses farm information to provide contextualized decision support.

---

## 5. Environmental Information

FarmOS may obtain environmental information from external data providers.

The current MVP uses Open-Meteo for environmental data.

Environmental information may include:

* Recent rainfall
* Forecast rainfall
* Temperature

Environmental data may contain inaccuracies, delays, gaps, or differences from actual local conditions.

FarmOS does not guarantee that external environmental information will always be complete, accurate, or available.

---

## 6. Risk Assessments

FarmOS generates risk assessments using defined decision rules and available environmental and farm information.

The current MVP uses deterministic rules.

A risk assessment may include:

* Risk level
* Risk score
* Confidence
* Contributing factors
* Recommendation
* Explanation

The assessment represents the output of the FarmOS decision model at the time it was generated.

Environmental conditions can change after an assessment has been produced.

Users should therefore avoid treating an assessment as a permanent prediction of future conditions.

---

## 7. Decision-Support Disclaimer

FarmOS is a **decision-support system**.

It is not intended to replace:

* Farmers' own judgment
* Local knowledge
* Agricultural professionals
* Extension services
* Other appropriate sources of agricultural guidance

FarmOS recommendations are not guarantees of crop performance, yield, water availability, or other agricultural outcomes.

Users remain responsible for decisions made on their farms.

---

## 8. No Guarantee of Agricultural Outcomes

FarmOS does not guarantee that following a recommendation will:

* Prevent crop damage
* Prevent water stress
* Increase crop yield
* Prevent agricultural losses
* Produce a particular harvest
* Accurately predict future environmental conditions

Agricultural outcomes depend on many factors that may not be represented in the current MVP.

These may include:

* Soil conditions
* Local weather variation
* Pest and disease pressure
* Farming practices
* Water availability
* Crop variety
* Management decisions
* Extreme weather
* Other environmental conditions

---

## 9. User Responsibilities

Users agree to use FarmOS responsibly.

Users should:

* Provide appropriate farm information.
* Review assessment explanations.
* Consider local conditions.
* Use professional or local agricultural guidance where appropriate.
* Avoid relying solely on an automated assessment for important agricultural decisions.
* Keep account credentials secure.
* Report significant application problems where appropriate.

Users should not intentionally provide misleading information for the purpose of manipulating system behavior.

---

## 10. Prohibited Use

Users must not use FarmOS to:

* Gain unauthorized access to accounts or resources.
* Circumvent security controls.
* Interfere with the availability or operation of the service.
* Attempt to access another user's private information.
* Deliberately submit malicious or abusive requests.
* Misrepresent FarmOS recommendations as guaranteed professional advice.
* Use the service for unlawful purposes.

Nothing in these Terms is intended to prevent legitimate security research conducted with appropriate authorization.

---

## 11. Intellectual Property

FarmOS, including its software, documentation, interface, design, and original project materials, may contain intellectual property belonging to the project creators or applicable contributors.

Unless a separate license or written permission states otherwise, users should not assume that project materials may be copied, redistributed, modified, or commercially exploited without permission.

Third-party software and services remain subject to their respective licenses and terms.

---

## 12. Open-Source and Third-Party Components

FarmOS may depend on open-source software and external services.

Examples include technologies used for:

* Web application development
* Backend services
* Database operations
* Authentication
* Environmental data

Third-party components are governed by their own applicable licenses and terms.

FarmOS does not claim ownership of third-party software or data.

---

## 13. External Services

FarmOS may depend on external services to provide functionality.

External services may experience:

* Downtime
* Rate limits
* Data changes
* Network failures
* Service interruptions
* Changes to their APIs
* Changes to their own terms

FarmOS cannot guarantee continuous availability or uninterrupted operation of third-party services.

---

## 14. Availability

The current FarmOS MVP is primarily a development and demonstration system.

The project does not guarantee:

* Continuous availability
* Uninterrupted service
* Permanent data retention
* Production-scale performance
* Immediate recovery from failures

Production deployments may introduce additional availability, backup, monitoring, and recovery measures.

---

## 15. Data and Privacy

FarmOS may process information associated with:

* User accounts
* Farms
* Farm locations
* Risk assessments
* Farmer feedback

The handling of this information is described in the FarmOS Privacy Policy.

Users should review the Privacy Policy to understand how information is intended to be handled.

---

## 16. Assessment History and Feedback

FarmOS may retain risk assessments and farmer feedback to support assessment history and system evaluation.

Feedback does not automatically modify the decision engine in the current MVP.

Future versions may use accumulated information for controlled evaluation or improvement.

Any future use of stored information should remain subject to applicable privacy, security, and data-management requirements.

---

## 17. Security

FarmOS is designed to include security controls such as:

* Password hashing
* Authentication
* Authorization
* Farm ownership checks
* Input validation

Users must not attempt to bypass these controls.

No software system can guarantee absolute security.

Production deployments should implement additional security controls appropriate to their environment.

---

## 18. Changes to the Service

FarmOS may evolve over time.

Changes may include:

* New features
* New risk models
* New environmental-data sources
* Changes to the frontend
* Changes to the API
* Security improvements
* Changes to data-handling practices

Features may be added, modified, or removed as the project develops.

---

## 19. Changes to These Terms

These Terms and Conditions may be updated as FarmOS evolves.

Updates may be necessary because of:

* New functionality
* Changes to the service
* Changes to external providers
* Security requirements
* Legal requirements
* Changes from an MVP to a production deployment

The **Last Updated** date should be revised whenever substantive changes are made.

---

## 20. Limitation of Liability

To the extent permitted by applicable law, FarmOS and its contributors should not be treated as guaranteeing agricultural, financial, environmental, or other outcomes resulting from use of the system.

Users remain responsible for evaluating FarmOS information and making decisions appropriate to their circumstances.

Nothing in these Terms is intended to exclude or limit liability where such exclusion or limitation would be prohibited by applicable law.

---

## 21. No Professional Advice

FarmOS provides automated decision-support information.

Information produced by the system should not automatically be considered:

* Professional agricultural advice
* Financial advice
* Legal advice
* Emergency advice
* A guarantee of environmental conditions

Users should seek appropriate qualified advice where the circumstances require it.

---

## 22. Responsible Use

FarmOS is designed to support human decision-making.

The intended relationship is:

```text
FarmOS Information
       ↓
User Evaluation
       ↓
Local Knowledge
       ↓
Appropriate Guidance
       ↓
Human Decision
```

The system should not be treated as an autonomous agricultural decision-maker.

---

## 23. Current MVP Limitations

The current MVP has a deliberately limited scope.

It does not provide a complete agricultural management platform.

Current limitations include:

* A primary focus on water-related risk.
* A primarily maize-focused decision model.
* A limited number of environmental variables.
* Simple deterministic rules.
* Dependence on an external environmental-data provider.
* Limited production-scale infrastructure.
* No automated irrigation control.
* No comprehensive pest and disease model.
* No automatic machine-learning retraining from farmer feedback.

These limitations should be considered when interpreting system results.

---

## 24. Future Development

Future versions of FarmOS may introduce:

* Additional crops
* Additional agricultural risks
* Soil information
* Satellite observations
* IoT sensors
* Historical climate information
* Improved uncertainty estimation
* Machine-learning models
* Additional environmental providers
* Production-scale infrastructure

Future functionality may require corresponding updates to these Terms and Conditions.

---

## 25. Termination or Restriction of Access

Where FarmOS is operated as an account-based service, access may be restricted or terminated when necessary to:

* Protect the system
* Protect users
* Address security concerns
* Prevent abuse
* Comply with applicable requirements

A production service should define specific account termination and data-handling procedures.

---

## 26. Governing Law

The applicable law governing a production FarmOS service should be specified by the organization operating the service and should reflect the jurisdiction in which the service is provided.

This MVP document does not claim to establish a specific governing jurisdiction.

Before commercial or public deployment, this section should be reviewed and finalized appropriately.

---

## 27. Contact

A production deployment of FarmOS should provide an official contact method for:

* General questions
* Account issues
* Privacy concerns
* Security concerns
* Service-related concerns

Until an operating organization and official contact process are established, this document should be treated as the project's terms-and-conditions baseline rather than a finalized commercial legal agreement.

---

## 28. Acceptance

Where FarmOS is deployed as a service requiring acceptance of terms, users should be presented with the applicable Terms and Conditions before or during account creation or service use, as appropriate to the deployment and applicable law.

The production implementation should maintain an appropriate record of the applicable version of the Terms where required.

---

## 29. Summary

FarmOS provides explainable agricultural decision support based on available farm and environmental information.

Users acknowledge that:

* FarmOS provides decision support rather than guaranteed outcomes.
* Environmental information may be incomplete or inaccurate.
* Risk assessments represent the conditions and rules available at the time of assessment.
* Users remain responsible for agricultural decisions.
* User and farm information is subject to the FarmOS Privacy Policy.
* The MVP has defined technical and functional limitations.

FarmOS is intended to provide a transparent foundation for agricultural decision support while maintaining human judgment, responsible use, security, and future extensibility.
