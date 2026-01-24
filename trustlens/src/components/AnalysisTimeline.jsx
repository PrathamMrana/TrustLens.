import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { ANALYSIS_STEPS } from '../utils/constants';

const AnalysisTimeline = ({ currentStepId, completedstepIds }) => {
    return (
        <div className="w-full max-w-3xl mx-auto my-8 space-y-4">
            <div className="flex items-center justify-between mb-6 px-2">
                <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">Analysis Progress</h3>
                <span className="text-xs text-slate-600 font-mono">
                    STAGE {currentStepId || completedstepIds.length} OF {ANALYSIS_STEPS.length}
                </span>
            </div>

            <div className="relative">
                {/* Vertical connection line */}
                <div className="absolute left-6 top-4 bottom-4 w-px bg-slate-800 z-0"></div>

                <div className="space-y-6 relative z-10">
                    {ANALYSIS_STEPS.map((step) => {
                        const isCompleted = completedstepIds.includes(step.id);
                        const isActive = currentStepId === step.id;
                        const isPending = !isActive && !isCompleted;

                        return (
                            <motion.div
                                key={step.id}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className={`flex items-center gap-4 p-3 rounded-lg transition-colors border border-transparent
                            ${isActive ? 'bg-blue-500/5 border-blue-500/10' : ''}
                        `}
                            >
                                <div className="flex-shrink-0 flex items-center justify-center w-12">
                                    {isCompleted ? (
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                        >
                                            <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                                        </motion.div>
                                    ) : isActive ? (
                                        <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
                                    ) : (
                                        <Circle className="w-6 h-6 text-slate-700" />
                                    )}
                                </div>

                                <div className="flex-grow">
                                    <p className={`text-sm font-medium transition-colors
                                ${isActive ? 'text-blue-300' : isCompleted ? 'text-slate-300' : 'text-slate-600'}
                            `}>
                                        {step.label}
                                    </p>
                                    {isActive && (
                                        <motion.p
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            className="text-xs text-blue-500/60 mt-1 font-mono"
                                        >
                                            Processing...
                                        </motion.p>
                                    )}
                                </div>
                            </motion.div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default AnalysisTimeline;
