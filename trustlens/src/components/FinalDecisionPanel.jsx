import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, ShieldAlert, FileSearch, Lock } from 'lucide-react';

const DECISION_CONFIG = {
    SAFE: {
        color: "text-logic",
        bg: "bg-logic/10",
        border: "border-logic/30",
        icon: ShieldCheck,
        title: "SAFE TO PROCEED",
        description: "All agents have reached a high-confidence consensus. No critical risks or logic errors were detected."
    },
    MANUAL_REVIEW: {
        color: "text-uncertainty",
        bg: "bg-uncertainty/10",
        border: "border-uncertainty/30",
        icon: Lock,
        title: "MANUAL REVIEW REQUIRED",
        description: "The system intentionally refused to make an automated decision due to conflicting agent reports."
    },
    RISK: {
        color: "text-security",
        bg: "bg-security/10",
        border: "border-security/30",
        icon: ShieldAlert,
        title: "HIGH RISK — ESCALATION RECOMMENDED",
        description: "Critical security vulnerabilities were detected with high confidence. Deployment is strongly discouraged."
    }
};

const FinalDecisionPanel = ({ decision }) => {
    if (!decision) return null;

    const config = DECISION_CONFIG[decision] || DECISION_CONFIG.MANUAL_REVIEW;
    const Icon = config.icon;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className={`w-full max-w-4xl mx-auto my-8 p-8 rounded-card border ${config.border} ${config.bg} relative overflow-hidden text-center`}
        >
            {/* Background decoration */}
            <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 blur-[80px] rounded-full opacity-20 pointer-events-none ${decision === 'SAFE' ? 'bg-logic' : decision === 'RISK' ? 'bg-security' : 'bg-uncertainty'}`} />

            <div className="relative z-10 flex flex-col items-center">
                <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, damping: 15 }}
                    className={`p-4 rounded-full border mb-6 bg-surface ${config.border}`}
                >
                    <Icon className={`w-10 h-10 ${config.color}`} />
                </motion.div>

                <h2 className={`text-2xl md:text-3xl font-bold mb-3 tracking-tight ${config.color}`}>
                    {config.title}
                </h2>

                <p className={`text-text-secondary max-w-2xl text-lg leading-relaxed`}>
                    {config.description}
                </p>

                {decision === 'MANUAL_REVIEW' && (
                    <div className="mt-8 flex gap-4">
                        <button className="px-6 py-2.5 rounded-lg bg-surface border border-border text-sm font-medium text-primary hover:bg-secondary transition-colors shadow-soft">
                            View Divergence Map
                        </button>
                        <button className="px-6 py-2.5 rounded-lg bg-uncertainty hover:bg-purple-600 text-white text-sm font-medium transition-colors shadow-glow-uncertainty">
                            Start Human Review
                        </button>
                    </div>
                )}
            </div>
        </motion.div>
    );
};

export default FinalDecisionPanel;
