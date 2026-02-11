
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:10000";
const CLEAN_BASE_URL = BASE_URL.replace(/\/$/, "");
const API_URL = CLEAN_BASE_URL.endsWith("/api") ? CLEAN_BASE_URL : `${CLEAN_BASE_URL}/api`;

export const APP_CONFIG = {
    name: "TrustLens",
    subtitle: "Multi-Agent AI Code Review Orchestrator",
    version: "v1.0.0-beta",
    API_BASE_URL: API_URL,
};

export const ANALYSIS_STEPS = [
    { id: 1, label: "Reading code snapshot" },
    { id: 2, label: "Extracting structural features" },
    { id: 3, label: "Running Security Agent" },
    { id: 4, label: "Running Logic Agent" },
    { id: 5, label: "Running Quality Agent" },
    { id: 6, label: "Cross-agent consistency check" },
    { id: 7, label: "Decision synthesis" },
];

export const MOCK_ANALYSIS_TIME_MS = 50; // Analysis Speed: Instant
