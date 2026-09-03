const form = document.getElementById("risk-form");

const result = document.getElementById("result");
const error = document.getElementById("error");

const riskLevel = document.getElementById("risk-level");
const score = document.getElementById("score");
const confidence = document.getElementById("confidence");
const factors = document.getElementById("factors");
const recommendation = document.getElementById("recommendation");
const explanation = document.getElementById("explanation");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    result.classList.add("hidden");
    error.classList.add("hidden");

    const latitude = Number(
        document.getElementById("latitude").value
    );

    const longitude = Number(
        document.getElementById("longitude").value
    );

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/water-risk",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude
                })
            }
        );

        if (!response.ok) {
            throw new Error("FarmOS API request failed.");
        }

        const data = await response.json();

        riskLevel.textContent = data.risk_level;
        score.textContent = data.score;
        confidence.textContent = data.confidence;

        factors.innerHTML = "";

        data.factors.forEach((factor) => {
            const item = document.createElement("li");
            item.textContent = factor;
            factors.appendChild(item);
        });

        recommendation.textContent = data.recommendation;
        explanation.textContent = data.explanation;

        result.classList.remove("hidden");
    } catch (err) {
        error.textContent =
            "Unable to connect to the FarmOS API. Make sure the backend is running.";

        error.classList.remove("hidden");
    }
});