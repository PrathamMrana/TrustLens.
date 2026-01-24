import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LiveAnalysisPanel from '../components/LiveAnalysisPanel';
import AnalysisStatusCard from '../components/AnalysisStatusCard';
import AnalysisLogs from '../components/AnalysisLogs';
import AgentCard from '../components/AgentCard';
import KeyInsights from '../components/KeyInsights';
import OverallOutcomePanel from '../components/OverallOutcomePanel';
import ConflictPanel from '../components/ConflictPanel';
import FinalDecisionPanel from '../components/FinalDecisionPanel';
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
        analysisId
    } = useAnalysis();

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
                        {/* Overall Outcome Panel - Top of results */}
                        {status === 'COMPLETE' && (
                            <OverallOutcomePanel overall={overall} />
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
                                            <div className={`text-sm font-bold ${agent.risk === 'high' ? 'text-security' :
                                                agent.risk === 'medium' ? 'text-quality' : 'text-logic'
                                                }`}>
                                                {agent.risk === 'high' ? 'CRITICAL' : agent.risk === 'medium' ? 'WARNING' : 'SAFE'}
                                            </div>
                                            <div className="text-xs text-muted mt-1">
                                                {agent.confidence}% Conf. • {agent.findingsCount} hints
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

                    {/* Conflict & Decision - Only show when complete */}
                    {status === 'COMPLETE' && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.5 }}
                            className="space-y-6 pt-8 border-t border-white/5"
                        >
                            <ConflictPanel conflict={true} />
                            <FinalDecisionPanel decision="MANUAL_REVIEW" />
                        </motion.div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SessionPage;
