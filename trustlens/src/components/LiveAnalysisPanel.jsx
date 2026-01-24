import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Loader2, List } from 'lucide-react';
import { ANALYSIS_STEPS } from '../utils/constants';

const LiveAnalysisPanel = ({ status, currentStepId, completedMeasurements }) => {
    const [isHovered, setIsHovered] = useState(false);
    const isComplete = status === 'COMPLETE';

    return (
        <motion.div
            initial={{ width: 320, opacity: 1, x: 0 }}
            animate={{
                width: isComplete && !isHovered ? 48 : 320,
                opacity: 1,
                x: 0
            }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            className={`relative h-fit group transition-all`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* Hover Strip (Visible when collapsed) */}
            {isComplete && (
                <div className="absolute inset-y-0 left-0 w-12 h-full flex items-center justify-center cursor-e-resize z-20 hover:bg-white/5 transition-colors rounded-r-lg">
                    <List className="w-5 h-5 text-text-secondary opacity-50" />
                </div>
            )}

            {/* Main Content */}
            <motion.div
                className="overflow-hidden bg-background/95 border border-border rounded-lg shadow-soft backdrop-blur-md"
                animate={{
                    opacity: isComplete && !isHovered ? 0 : 1,
                    translateX: isComplete && !isHovered ? -20 : 0
                }}
                transition={{ duration: 0.5 }}
            >
                <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wider">Analysis Progress</h3>
                        <span className="text-xs text-muted font-mono">
                            {currentStepId ? `STAGE ${currentStepId}/5` : 'COMPLETE'}
                        </span>
                    </div>

                    <div className="relative pl-2">
                        {/* Vertical connection line */}
                        <div className="absolute left-[23px] top-4 bottom-4 w-px bg-border z-0"></div>

                        <div className="space-y-6 relative z-10">
                            {ANALYSIS_STEPS.map((step) => {
                                const isCompleted = completedMeasurements.includes(step.id);
                                const isActive = currentStepId === step.id;

                                return (
                                    <motion.div
                                        key={step.id}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className={`flex items-center gap-4 transition-colors`}
                                    >
                                        <div className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-background border border-border z-10">
                                            {isCompleted ? (
                                                <motion.div
                                                    initial={{ scale: 0 }}
                                                    animate={{ scale: 1 }}
                                                >
                                                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                                                </motion.div>
                                            ) : isActive ? (
                                                <Loader2 className="w-5 h-5 text-brand animate-spin" />
                                            ) : (
                                                <Circle className="w-5 h-5 text-muted/30" />
                                            )}
                                        </div>

                                        <div className="flex-grow">
                                            <p className={`text-sm font-medium transition-colors
                                            ${isActive ? 'text-brand' : isCompleted ? 'text-primary' : 'text-muted'}
                                        `}>
                                                {step.label}
                                            </p>
                                            {isActive && (
                                                <motion.p
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    className="text-xs text-brand/60 mt-0.5 font-mono"
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
            </motion.div>
        </motion.div>
    );
};

export default LiveAnalysisPanel;
