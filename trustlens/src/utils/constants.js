
export const APP_CONFIG = {
    name: "TrustLens",
    subtitle: "Multi-Agent AI Code Review Orchestrator",
    version: "v1.0.0-beta",
};

export const ANALYSIS_STEPS = [
    { id: 1, label: "Reading code snapshot" },
    { id: 2, label: "Extracting structural features" },
    { id: 3, label: "Running Security Agent" },
    { id: 4, label: "Running Logic Agent" },
    { id: 5, label: "Cross-agent consistency check" },
];

export const MOCK_ANALYSIS_TIME_MS = 2500; // Time per step for "deliberate speed"
