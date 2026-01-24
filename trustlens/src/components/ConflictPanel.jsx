import React from 'react';
import { motion } from 'framer-motion';
import { GitMerge, AlertCircle } from 'lucide-react';

const ConflictPanel = ({ conflict }) => {
    if (!conflict) return null;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            className="w-full max-w-4xl mx-auto my-8 relative"
        >
            {/* Glowing Connector Lines Visual */}
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-0.5 h-4 bg-gradient-to-b from-transparent to-uncertainty opacity-50"></div>

            <div className="bg-surface/50 border border-uncertainty/30 rounded-card p-0.5 relative overflow-hidden shadow-glow-uncertainty">
                {/* Background animated pulse */}
                <div className="absolute inset-0 bg-uncertainty/5 animate-pulse pointer-events-none" />

                <div className="relative z-10 bg-background/80 backdrop-blur-sm rounded-[12px] p-6 flex flex-col md:flex-row items-center md:items-start gap-5">

                    <div className="p-3 bg-uncertainty/10 rounded-full border border-uncertainty/20 flex-shrink-0">
                        <GitMerge className="w-6 h-6 text-uncertainty" />
                    </div>

                    <div className="flex-grow text-center md:text-left">
                        <h3 className="text-lg font-medium text-primary mb-2 flex items-center justify-center md:justify-start gap-2">
                            Conflict Detected
                            <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-uncertainty/20 text-uncertainty border border-uncertainty/30">
                                Action Required
                            </span>
                        </h3>

                        <p className="text-text-secondary text-sm leading-relaxed max-w-2xl">
                            <span className="text-security font-medium">Security Agent</span> and <span className="text-logic font-medium">Logic Agent</span> disagree on risk interpretation.
                            The system cannot auto-resolve this ambiguity without human context.
                        </p>

                        <div className="mt-4 flex flex-wrap gap-3 justify-center md:justify-start">
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-secondary border border-border text-xs text-muted">
                                <AlertCircle className="w-3.5 h-3.5" />
                                <span>Confidence Gap: 12%</span>
                            </div>
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-secondary border border-border text-xs text-muted">
                                <span>Source: Line 45-48</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default ConflictPanel;
