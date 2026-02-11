import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Shield, Brain, GitMerge, Search, ArrowRight } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';
import { Link } from 'react-router-dom';

const ConflictsPage = () => {
    const { report, results, status } = useAnalysis();

    const hasConflict = report?.disagreement_detected;
    const hasResults = results && results.length > 0;

    // Extract conflict details from real data
    const highRiskAgents = hasResults ? results.filter(r => r.risk === 'high' || r.risk === 'critical') : [];
    const safeAgents = hasResults ? results.filter(r => r.risk === 'low' || r.risk === 'none') : [];
    const hasRealDisagreement = highRiskAgents.length > 0 && safeAgents.length > 0;

    return (
        <div className="max-w-4xl mx-auto py-12 px-4">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-white mb-2">Inter-Agent Conflicts</h1>
                <p className="text-slate-400">
                    When expert agents disagree on risk, TrustLens escalates for human review rather than guessing.
                </p>
            </div>

            {status !== 'COMPLETE' ? (
                /* No analysis data yet */
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-8 rounded-xl border border-white/5 bg-surface/50 text-center"
                >
                    <GitMerge className="w-10 h-10 text-slate-600 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-slate-300 mb-2">No Active Analysis</h3>
                    <p className="text-sm text-slate-500 max-w-md mx-auto mb-6">
                        Run an analysis first to see if agents produce conflicting assessments.
                    </p>
                    <Link to="/analyze" className="inline-flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors cursor-pointer">
                        Start Analysis <ArrowRight className="w-4 h-4" />
                    </Link>
                </motion.div>
            ) : (hasConflict || hasRealDisagreement) ? (
                /* Real conflict detected */
                <div className="space-y-6">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="p-6 rounded-xl border border-uncertainty/30 bg-uncertainty/5 relative overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-uncertainty/5 animate-pulse pointer-events-none" />
                        <div className="relative z-10">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2.5 bg-uncertainty/10 rounded-full border border-uncertainty/20">
                                    <AlertTriangle className="w-5 h-5 text-uncertainty" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-white">Conflict Detected</h3>
                                    <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-uncertainty/20 text-uncertainty border border-uncertainty/30">
                                        Action Required
                                    </span>
                                </div>
                            </div>
                            <p className="text-sm text-slate-300 leading-relaxed mb-4">
                                Agents produced conflicting risk assessments. The Decision Agent applied a confidence penalty and escalated for human review.
                            </p>
                        </div>
                    </motion.div>

                    {/* Conflicting Agent Details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {highRiskAgents.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 }}
                                className="p-5 rounded-xl border border-red-500/20 bg-red-500/5"
                            >
                                <div className="flex items-center gap-2 mb-3">
                                    <Shield className="w-4 h-4 text-red-400" />
                                    <h4 className="text-sm font-bold text-red-400 uppercase tracking-wider">High / Critical Risk Assessment</h4>
                                </div>
                                {highRiskAgents.map(agent => (
                                    <div key={agent.name} className="mb-3 last:mb-0">
                                        <p className="text-sm font-medium text-white">{agent.name}</p>
                                        <p className="text-xs text-slate-400 mt-1">{agent.summary}</p>
                                        <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                                            <span>Analysis Confidence: {agent.confidence}%</span>
                                            <span>Findings: {agent.findingsCount}</span>
                                        </div>
                                    </div>
                                ))}
                            </motion.div>
                        )}

                        {safeAgents.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, x: 10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.2 }}
                                className="p-5 rounded-xl border border-emerald-500/20 bg-emerald-500/5"
                            >
                                <div className="flex items-center gap-2 mb-3">
                                    <Brain className="w-4 h-4 text-emerald-400" />
                                    <h4 className="text-sm font-bold text-emerald-400 uppercase tracking-wider">Low Risk Assessment</h4>
                                </div>
                                {safeAgents.map(agent => (
                                    <div key={agent.name} className="mb-3 last:mb-0">
                                        <p className="text-sm font-medium text-white">{agent.name}</p>
                                        <p className="text-xs text-slate-400 mt-1">{agent.summary}</p>
                                        <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                                            <span>Analysis Confidence: {agent.confidence}%</span>
                                            <span>Findings: {agent.findingsCount}</span>
                                        </div>
                                    </div>
                                ))}
                            </motion.div>
                        )}
                    </div>

                    <div className="p-4 rounded-lg border border-white/5 bg-surface/30 text-center">
                        <p className="text-xs text-slate-500">
                            The Decision Agent applies a <span className="text-uncertainty font-mono">20% penalty per conflict</span> (capped at 50%) to the overall confidence score when disagreements are detected.
                        </p>
                    </div>
                </div>
            ) : (
                /* No conflicts detected */
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-8 rounded-xl border border-emerald-500/20 bg-emerald-500/5 text-center"
                >
                    <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4">
                        <GitMerge className="w-6 h-6 text-emerald-400" />
                    </div>
                    <h3 className="text-lg font-medium text-emerald-300 mb-2">No Conflicts Detected</h3>
                    <p className="text-sm text-slate-400 max-w-md mx-auto">
                        All agents reached consensus on this analysis. The Decision Agent was able to produce a verdict without escalation.
                    </p>
                </motion.div>
            )}
        </div>
    );
};

export default ConflictsPage;
