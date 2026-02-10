import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LiveAnalysisPanel from '../components/LiveAnalysisPanel';
import AnalysisStatusCard from '../components/AnalysisStatusCard';
import AnalysisLogs from '../components/AnalysisLogs';
import AgentCard from '../components/AgentCard';
import KeyInsights from '../components/KeyInsights';
import UnifiedOutcomePanel from '../components/UnifiedOutcomePanel';
import { useAnalysis } from '../context/AnalysisContext';
import { motion, AnimatePresence } from 'framer-motion';

const SessionPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const {
        status,
        currentStepId,
        completedMeasurements,
        results,
        overall,
        analysisId,
        report
    } = useAnalysis();

    // Map backend decision values to FinalDecisionPanel keys
    const getDecisionKey = () => {
        if (!report?.final_decision) return null;
        const d = report.final_decision.toLowerCase();

        const risk = report.overall_risk_level?.toLowerCase();

        // Priority 1: High/Critical Risk overrides everything
        if (d.includes('manual_review_required') || d.includes('review_required') || risk === 'high' || risk === 'critical') {
            return 'RISK';
        }

        // Priority 2: Conflict or Low Confidence -> Manual Review (Uncertainty)
        if (report.disagreement_detected || (report.overall_confidence && report.overall_confidence < 0.7)) {
            return 'MANUAL_REVIEW';
        }

        // Priority 3: Caution
        if (d === 'proceed_with_caution' || risk === 'medium') {
            return 'CAUTION';
        }

        // Priority 4: Safe
        return 'SAFE';
    };

    // Redirect logic
    useEffect(() => {
        if (!analysisId && status === 'IDLE') {
            navigate('/analyze');
        }
    }, [analysisId, status, navigate]);

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex flex-col lg:flex-row gap-8 min-h-screen relative">
                {/* Live Sidebar - Collapses on complete */}
                <div className="lg:sticky lg:top-24 h-fit shrink-0 relative z-20 transition-all duration-700">
                    <LiveAnalysisPanel
                        status={status}
                        currentStepId={currentStepId}
                        completedMeasurements={completedMeasurements}
                    />
                </div>

                {/* Main Content Area - Expands when sidebar collapses */}
                <div className="flex-1 space-y-6 pb-20 min-w-0">
                    {/* Active Analysis State */}
                    {status === 'ANALYZING' && (!results || results.length < 5) && (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <div className="lg:col-span-2 py-8">
                                <AnalysisStatusCard currentStepId={currentStepId} />
                            </div>
                            <div className="lg:col-span-1 h-[400px] sticky top-24">
                                <AnalysisLogs />
                            </div>
                        </div>
                    )}

                    {/* Progressive Agent Cards */}
                    <div className="space-y-6">
                        {/* Unified Outcome Panel - Top of results */}
                        {status === 'COMPLETE' && (
                            <UnifiedOutcomePanel decision={getDecisionKey()} overall={overall} report={report} />
                        )}

                        {/* Key Insights - Only show when we have results */}
                        {status === 'COMPLETE' && results && results.length > 0 && (
                            <KeyInsights results={results} />
                        )}

                        {/* Agent Overview Grid - At a glance details */}
                        {status === 'COMPLETE' && results && (
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                <AnimatePresence>
                                    {results.map((agent, index) => (
                                        <motion.div
                                            key={`grid-${agent.name}`}
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            transition={{ delay: index * 0.1 }}
                                            className="p-3 rounded-lg border border-border bg-surface/30"
                                        >
                                            <div className="text-[10px] uppercase text-muted font-bold tracking-wider mb-1 truncate">{agent.name}</div>
                                            <div className={`text-sm font-bold ${(agent.risk === 'high' || agent.risk === 'critical') ? 'text-security' :
                                                agent.risk === 'medium' ? 'text-quality' : 'text-logic'
                                                }`}>
                                                {(agent.risk === 'high' || agent.risk === 'critical') ? 'CRITICAL' : agent.risk === 'medium' ? 'WARNING' : 'SAFE'}
                                            </div>
                                            <div className="text-xs text-muted mt-1">
                                                {agent.confidence}% Confidence • {agent.findingsCount} hints
                                            </div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                            </div>
                        )}

                        {/* Detailed Agent Cards */}
                        <AnimatePresence>
                            {results && results.map((agent, index) => (
                                <AgentCard key={agent.name} agent={agent} index={index} />
                            ))}
                        </AnimatePresence>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default SessionPage;
