import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

const OverallOutcomePanel = ({ overall }) => {
    if (!overall) return null;

    // Visual configuration based on risk
    const isHighRisk = overall.risk.toLowerCase() === 'high';
    const isSafe = overall.risk.toLowerCase() === 'low';

    const config = {
        color: isHighRisk ? 'text-security' : isSafe ? 'text-logic' : 'text-quality',
        bg: isHighRisk ? 'bg-security/10' : isSafe ? 'bg-logic/10' : 'bg-quality/10',
        border: isHighRisk ? 'border-security/30' : isSafe ? 'border-logic/30' : 'border-quality/30',
        glow: isHighRisk ? 'shadow-glow-security' : isSafe ? 'shadow-glow-logic' : 'shadow-glow-quality',
        label: isHighRisk ? 'CRITICAL RISK DETECTED' : isSafe ? 'SAFE TO PROCEED' : 'CAUTION ADVISED'
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className={`w-full rounded-card border ${config.border} bg-surface p-8 mb-8 relative overflow-hidden text-center shadow-soft`}
        >
            {/* Ambient Glow */}
            <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-64 h-24 ${config.bg} blur-[60px] opacity-20 pointer-events-none`} />

            <div className="relative z-10">
                <h2 className="text-xs font-mono uppercase tracking-[0.2em] text-text-secondary mb-4 opacity-70">
                    [ OVERALL REVIEW OUTCOME ]
                </h2>

                <div className={`text-4xl md:text-5xl font-bold mb-4 tracking-tight ${config.color}`}>
                    {config.label}
                </div>

                <div className="flex flex-col items-center justify-center gap-2">
                    <div className="flex items-end gap-2 text-primary">
                        <span className="text-sm font-medium uppercase text-muted tracking-wider mb-1">Overall Confidence</span>
                        <span className="text-2xl font-mono relative top-[2px]">{(overall.confidence * 100).toFixed(0)}%</span>
                    </div>

                    {/* Visual Confidence Bar */}
                    <div className="w-48 h-1.5 bg-secondary rounded-full overflow-hidden mt-1">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${overall.confidence * 100}%` }}
                            transition={{ duration: 1, delay: 0.5 }}
                            className={`h-full rounded-full ${isHighRisk ? 'bg-security' : isSafe ? 'bg-logic' : 'bg-quality'}`}
                        />
                    </div>
                </div>

                <p className="max-w-xl mx-auto mt-6 text-sm text-muted">
                    This reflects the system’s aggregated confidence and risk based on expert agent analysis.
                </p>
            </div>
        </motion.div>
    );
};

export default OverallOutcomePanel;
