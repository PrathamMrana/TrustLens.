import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Brain, Zap, Search, FileCode, Binary, GitMerge, Scale } from 'lucide-react';
import { ANALYSIS_STEPS } from '../utils/constants';

const STEP_CONFIG = {
    1: { icon: FileCode, color: "text-blue-400", border: "border-blue-500/30", bg: "bg-blue-500/10", glow: "shadow-blue-500/20", subtext: "Ingesting codebase..." },
    2: { icon: Binary, color: "text-purple-400", border: "border-purple-500/30", bg: "bg-purple-500/10", glow: "shadow-purple-500/20", subtext: "Building AST & extracting features..." },
    3: { icon: Shield, color: "text-security", border: "border-security/30", bg: "bg-security/10", glow: "shadow-glow-security", subtext: "Scanning for CVEs & vulnerabilities..." },
    4: { icon: Brain, color: "text-logic", border: "border-logic/30", bg: "bg-logic/10", glow: "shadow-glow-logic", subtext: "Verifying business logic integrity..." },
    5: { icon: Search, color: "text-quality", border: "border-quality/30", bg: "bg-quality/10", glow: "shadow-glow-quality", subtext: "Evaluating code quality metrics..." },
    6: { icon: Scale, color: "text-accent-cyan", border: "border-cyan-500/30", bg: "bg-cyan-500/10", glow: "shadow-cyan-500/20", subtext: "Checking cross-agent consistency..." },
    7: { icon: GitMerge, color: "text-uncertainty", border: "border-uncertainty/30", bg: "bg-uncertainty/10", glow: "shadow-glow-uncertainty", subtext: "Synthesizing final decision..." },
};

const AnalysisStatusCard = ({ currentStepId }) => {
    const config = STEP_CONFIG[currentStepId] || STEP_CONFIG[1];
    const StepIcon = config.icon;
    const stepLabel = ANALYSIS_STEPS.find(s => s.id === currentStepId)?.label || "Initializing...";

    return (
        <motion.div
            className="w-full max-w-xl mx-auto"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
        >
            <div className={`relative overflow-hidden rounded-card border ${config.border} bg-surface/50 backdrop-blur-md p-8 text-center shadow-soft`}>

                {/* Ambient Glow */}
                <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-32 h-32 ${config.bg} blur-[60px] rounded-full opacity-40 animate-pulse`} />

                <div className="relative z-10 flex flex-col items-center">
                    {/* Icon Circle */}
                    <div className={`w-20 h-20 rounded-full border ${config.border} ${config.bg} flex items-center justify-center mb-6 relative`}>
                        <div className={`absolute inset-0 rounded-full border border-white/5 animate-[spin_3s_linear_infinite]`} />
                        <StepIcon className={`w-10 h-10 ${config.color}`} />
                    </div>

                    <h3 className="text-xl font-bold text-primary mb-2">
                        {stepLabel}
                    </h3>

                    <p className="text-sm text-text-secondary font-mono tracking-wide">
                        {config.subtext}
                    </p>

                    {/* Progress Bar */}
                    <div className="w-full max-w-xs mt-8 h-1 bg-secondary rounded-full overflow-hidden">
                        <motion.div
                            className={`h-full ${config.bg.replace('/10', '')} ${config.color.replace('text-', 'bg-')}`}
                            initial={{ x: '-100%' }}
                            animate={{ x: '100%' }}
                            transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                        />
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default AnalysisStatusCard;
