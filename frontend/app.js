const API_BASE = "http" + String.fromCharCode(58, 47, 47) + "127.0.0.1:8000";

const authCard = document.getElementById("auth-card");
const appCard = document.getElementById("app-card");
const authForm = document.getElementById("auth-form");
const farmForm = document.getElementById("farm-form");
const feedbackForm = document.getElementById("feedback-form");

const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");

const farmSelect = document.getElementById("farm-select");
const selectedFarm = document.getElementById("selected-farm");
const assessButton = document.getElementById("assess-button");

const result = document.getElementById("result");
const feedbackCard = document.getElementById("feedback-card");
const feedbackSuccess = document.getElementById("feedback-success");
const error = document.getElementById("error");

const riskLevel = document.getElementById("risk-level");
const score = document.getElementById("score");
const confidence = document.getElementById("confidence");
const context = document.getElementById("context");
const factors = document.getElementById("factors");
const recommendation = document.getElementById("recommendation");
const explanation = document.getElementById("explanation");

const userEmail = document.getElementById("user-email");

let farms = [];
let currentAssessmentId = null;

function getToken() {
    return localStorage.getItem("farmos_access_token");
}

function setToken(token) {
    localStorage.setItem("farmos_access_token", token);
}

function clearToken() {
    localStorage.removeItem("farmos_access_token");
}

function showError(message) {
    error.textContent = message;
    error.classList.remove("hidden");
}

function clearError() {
    error.textContent = "";
    error.classList.add("hidden");
}

function showAuthenticatedApp() {
    authCard.classList.add("hidden");
    appCard.classList.remove("hidden");
}

function showLogin() {
    authCard.classList.remove("hidden");
    appCard.classList.add("hidden");
    result.classList.add("hidden");
    feedbackCard.classList.add("hidden");
}

async function apiRequest(path, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    const token = getToken();

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers
    });

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const detail =
            data && data.detail
                ? data.detail
                : "FarmOS API request failed.";

        throw new Error(detail);
    }

    return data;
}

async function loadCurrentUser() {
    const user = await apiRequest("/me");
    userEmail.textContent = user.email;
}

async function loadFarms() {
    farms = await apiRequest("/farms");

    farmSelect.innerHTML = '<option value="">Select a farm</option>';

    farms.forEach((farm) => {
        const option = document.createElement("option");

        option.value = farm.id;
        option.textContent = `${farm.name} — ${farm.crop}, ${farm.growth_stage}`;

        farmSelect.appendChild(option);
    });

    updateSelectedFarm();
}

function updateSelectedFarm() {
    const farmId = Number(farmSelect.value);
    const farm = farms.find((item) => item.id === farmId);

    if (!farm) {
        selectedFarm.textContent = "Select a farm to begin.";
        assessButton.disabled = true;
        return;
    }

    selectedFarm.textContent =
        `${farm.name} — ${farm.crop}, ${farm.growth_stage} ` +
        `(${farm.latitude}, ${farm.longitude})`;

    assessButton.disabled = false;
}

authForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();

    try {
        const data = await apiRequest("/login", {
            method: "POST",
            body: JSON.stringify({
                email: emailInput.value.trim(),
                password: passwordInput.value
            })
        });

        setToken(data.access_token);

        await loadCurrentUser();
        await loadFarms();

        showAuthenticatedApp();

        authForm.reset();
    } catch (err) {
        showError(err.message);
    }
});

document.getElementById("register-button").addEventListener(
    "click",
    async () => {
        clearError();

        try {
            await apiRequest("/register", {
                method: "POST",
                body: JSON.stringify({
                    email: emailInput.value.trim(),
                    password: passwordInput.value
                })
            });

            const data = await apiRequest("/login", {
                method: "POST",
                body: JSON.stringify({
                    email: emailInput.value.trim(),
                    password: passwordInput.value
                })
            });

            setToken(data.access_token);

            await loadCurrentUser();
            await loadFarms();

            showAuthenticatedApp();

            authForm.reset();
        } catch (err) {
            showError(err.message);
        }
    }
);

farmForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();

    try {
        await apiRequest("/farms", {
            method: "POST",
            body: JSON.stringify({
                name: document.getElementById("farm-name").value.trim(),
                latitude: Number(
                    document.getElementById("latitude").value
                ),
                longitude: Number(
                    document.getElementById("longitude").value
                ),
                crop: document.getElementById("crop").value,
                growth_stage:
                    document.getElementById("growth-stage").value
            })
        });

        farmForm.reset();

        await loadFarms();

        if (farms.length > 0) {
            farmSelect.value = String(farms[farms.length - 1].id);
            updateSelectedFarm();
        }
    } catch (err) {
        showError(err.message);
    }
});

farmSelect.addEventListener("change", () => {
    clearError();

    result.classList.add("hidden");
    feedbackCard.classList.add("hidden");
    currentAssessmentId = null;
    updateSelectedFarm();
});

assessButton.addEventListener("click", async () => {
    clearError();

    const farmId = Number(farmSelect.value);

    if (!farmId) {
        showError("Please select a farm first.");
        return;
    }

    assessButton.disabled = true;

    try {
        const data = await apiRequest("/water-risk", {
            method: "POST",
            body: JSON.stringify({
                farm_id: farmId
            })
        });

        currentAssessmentId = data.assessment_id;

        riskLevel.textContent = data.risk_level;
        score.textContent = data.score;
        confidence.textContent = data.confidence;
        context.textContent = data.context;

        factors.innerHTML = "";

        data.factors.forEach((factor) => {
            const item = document.createElement("li");
            item.textContent = factor;
            factors.appendChild(item);
        });

        recommendation.textContent = data.recommendation;
        explanation.textContent = data.explanation;

        result.classList.remove("hidden");

        feedbackForm.reset();
        feedbackSuccess.classList.add("hidden");
        feedbackCard.classList.remove("hidden");
    } catch (err) {
        showError(err.message);
    } finally {
        assessButton.disabled = false;
    }
});

feedbackForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();

    if (!currentAssessmentId) {
        showError("No risk assessment is available for feedback.");
        return;
    }

    try {
        await apiRequest(
            `/risk-assessments/${currentAssessmentId}/feedback`,
            {
                method: "POST",
                body: JSON.stringify({
                    farmer_action:
                        document.getElementById("farmer-action").value.trim(),
                    observed_result:
                        document.getElementById("observed-result").value.trim()
                })
            }
        );

        feedbackForm.reset();

        feedbackSuccess.textContent =
            "Feedback recorded successfully for this risk assessment.";

        feedbackSuccess.classList.remove("hidden");
    } catch (err) {
        showError(err.message);
    }
});

document.getElementById("logout-button").addEventListener(
    "click",
    () => {
        clearToken();

        farms = [];
        currentAssessmentId = null;

        farmSelect.innerHTML =
            '<option value="">Select a farm</option>';

        result.classList.add("hidden");
        feedbackCard.classList.add("hidden");

        showLogin();
        clearError();
    }
);

async function initialize() {
    const token = getToken();

    if (!token) {
        showLogin();
        return;
    }

    try {
        await loadCurrentUser();
        await loadFarms();
        showAuthenticatedApp();
    } catch {
        clearToken();
        showLogin();
        showError(
            "Your session is no longer valid. Please log in again."
        );
    }
}

initialize();
