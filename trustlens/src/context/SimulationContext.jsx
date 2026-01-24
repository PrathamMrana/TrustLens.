import React, { createContext, useContext, useState, useEffect } from 'react';
import { ANALYSIS_STEPS, MOCK_ANALYSIS_TIME_MS } from '../utils/constants';

const SimulationContext = createContext(null);

export const useSimulation = () => useContext(SimulationContext);

// Mock outcome data (same as before, but centralized)
export const MOCK_RESULTS = [
    {
        name: "Security Agent",
        risk: "high",
        confidence: 88,
        findingsCount: 3,
        summary: "Critical SQL injection vulnerability detected in the query construction. Input sanitization is missing for the 'userId' parameter."
    },
    {
        name: "Logic Agent",
        risk: "low",
        confidence: 94,
        findingsCount: 0,
        summary: "Code logic adheres to functional requirements. No infinite loops or unreachable code blocks detected. Control flow is valid."
    },
    {
        name: "Quality Agent",
        risk: "medium",
        confidence: 76,
        findingsCount: 5,
        summary: "Several complexity thresholds exceeded. Function 'processUserData' has high cyclomatic complexity (14). Recommended refactoring."
    },
    {
        name: "Feature Agent",
        risk: "low",
        confidence: 91,
        findingsCount: 1,
        summary: "Identified 'User Authentication' pattern. Implementation matches standard OIDC flow."
    }
];

export const MOCK_OVERALL = {
    risk: "high",
    confidence: 0.78,
    summary: "The system’s aggregated confidence based on expert agent analysis."
};

export const SimulationProvider = ({ children }) => {
    const [status, setStatus] = useState('IDLE'); // IDLE, ANALYZING, COMPLETE
    const [currentStepId, setCurrentStepId] = useState(0);
    const [completedMeasurements, setCompletedMeasurements] = useState([]);
    const [results, setResults] = useState(null);
    const [analysisType, setAnalysisType] = useState('deep'); // 'quick' or 'deep'
    const [allowSuggestions, setAllowSuggestions] = useState(false);
    const [sessionId, setSessionId] = useState(null);

    const startAnalysis = async (input, type = 'deep', suggestions = false) => {
        setStatus('ANALYZING');
        setResults(null);
        setCurrentStepId(0);
        setCompletedMeasurements([]);
        setAnalysisType(type);
        setAllowSuggestions(suggestions);

        // Create a mock session ID
        const newSessionId = Math.random().toString(36).substring(7);
        setSessionId(newSessionId);

        // Animate through steps
        for (const step of ANALYSIS_STEPS) {
            setCurrentStepId(step.id);

            // Variable delay based on type
            const baseTime = type === 'quick' ? 800 : MOCK_ANALYSIS_TIME_MS;
            const delay = baseTime + (Math.random() * 1000);
            await new Promise(resolve => setTimeout(resolve, delay));

            setCompletedMeasurements(prev => [...prev, step.id]);

            // Progressive disclosure logic
            if (step.label.includes("Security Agent")) {
                setResults(prev => [...(prev || []), MOCK_RESULTS.find(r => r.name === "Security Agent")]);
            } else if (step.label.includes("Logic Agent")) {
                setResults(prev => [...(prev || []), MOCK_RESULTS.find(r => r.name === "Logic Agent")]);
            } else if (step.label.includes("structural features")) {
                // Maybe show Quality/Feature here or wait? Let's show Feature early
                setResults(prev => [...(prev || []), MOCK_RESULTS.find(r => r.name === "Feature Agent")]);
            }
        }

        // Final clean up and remaining agents
        const currentlyShown = results || []; // This might be stale in closure, beware. 
        // Actually, safer to just set all at the end to ensure consistency, 
        // OR rely on the state updates. 
        // Let's sets the Quality agent at the end if not shown.
        setResults(MOCK_RESULTS);
        setStatus('COMPLETE');
    };

    const resetSimulation = () => {
        setStatus('IDLE');
        setResults(null);
        setCurrentStepId(0);
        setCompletedMeasurements([]);
        setSessionId(null);
    };

    return (
        <SimulationContext.Provider value={{
            status,
            currentStepId,
            completedMeasurements,
            results,
            overall: MOCK_OVERALL,
            analysisType,
            allowSuggestions,
            sessionId,
            startAnalysis,
            resetSimulation
        }}>
            {children}
        </SimulationContext.Provider>
    );
};
