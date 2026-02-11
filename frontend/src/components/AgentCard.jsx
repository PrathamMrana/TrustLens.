import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Brain, Zap, Search, ChevronRight, ChevronDown, GitMerge } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const RISK_CONFIG = {
    critical: {
        color: "text-security",
        bg: "bg-surface",
        border: "border-security/30",
        glow: "shadow-glow-security",
        fill: "bg-security"
    },
    high: {
        color: "text-security",
        bg: "bg-surface",
        border: "border-security/30",
        glow: "shadow-glow-security",
        fill: "bg-security"
    },
    medium: {
        color: "text-quality",
        bg: "bg-surface",
        border: "border-quality/30",
        glow: "shadow-glow-quality",
        fill: "bg-quality"
    },
    low: {
        color: "text-logic",
        bg: "bg-surface",
        border: "border-logic/30",
        glow: "shadow-glow-logic",
        fill: "bg-logic"
    },
    unknown: {
        color: "text-uncertainty",
        bg: "bg-surface",
        border: "border-uncertainty/30",
        glow: "shadow-glow-uncertainty",
        fill: "bg-uncertainty"
    }
};

const ICONS = {
    "Security Agent": Shield,
    "Security Analysis": Shield,
    "Logic Agent": Brain,
    "Logic Analysis": Brain,
    "Quality Agent": Search,
    "Code Quality": Search,
    "Feature Agent": Zap,
    "Feature Extraction": Zap,
    "Decision Agent": GitMerge,
    "Decision": GitMerge,
};

const AgentCard = ({ agent, index }) => {
    const [expanded, setExpanded] = useState(false);
    const Icon = ICONS[agent.name] || Brain;
    const config = RISK_CONFIG[agent.risk] || RISK_CONFIG.unknown;

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`
                w-full group rounded-card border ${config.border} ${config.bg} p-1
                overflow-hidden transition-all duration-300
                hover:shadow-lg hover:scale-[1.01] hover:border-opacity-50
                focus-within:ring-2 focus-within:ring-blue-500/50 focus-within:ring-offset-2 focus-within:ring-offset-background
            `}
        >
            <div
                onClick={() => setExpanded(!expanded)}
                className="p-5 rounded-[12px] bg-background/50 hover:bg-background/80 transition-colors cursor-pointer relative overflow-hidden"
            >
                {/* Subtle Glow on active state */}
                <div className={`absolute inset-0 opacity-0 transition-opacity duration-700 ${config.glow} opacity-[0.05] pointer-events-none`} />

                <div className="flex justify-between items-start relative z-10">
                    <div className="flex items-center gap-4">
                        <div className={`p-2.5 rounded-lg border border-white/5 bg-secondary flex items-center justify-center`}>
                            <Icon className={`w-5 h-5 ${config.color}`} />
                        </div>
                        <div>
                            <h4 className="text-sm font-semibold text-primary">{agent.name}</h4>
                            <div className={`text-xs font-mono uppercase tracking-wider mt-1 opacity-80 ${config.color}`}>
                                {(agent.risk === 'high' || agent.risk === 'critical') ? 'Critical Risk' : agent.risk === 'medium' ? 'Warning' : 'Safe to Proceed'}
                            </div>
                        </div>
                    </div>

                    <div className="text-right">
                        <div className="text-[10px] text-muted uppercase font-medium mb-1.5 tracking-wider">Analysis Confidence</div>
                        <div className="flex items-center gap-2 justify-end">
                            <div className="w-24 h-1.5 bg-secondary rounded-full overflow-hidden border border-white/5">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${agent.confidence}%` }}
                                    transition={{ duration: 1.2, ease: "circOut", delay: 0.2 }}
                                    className={`h-full rounded-full ${config.fill}`}
                                />
                            </div>
                            <span className="text-xs font-mono text-text-secondary">{agent.confidence}%</span>
                        </div>
                    </div>
                </div>

                <div className="mt-4 flex items-center justify-between">
                    <p className="text-sm text-text-secondary leading-relaxed line-clamp-1 opacity-90">
                        {agent.summary}
                    </p>
                    <button className="text-muted hover:text-primary transition-colors">
                        {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </button>
                </div>
            </div>

            {/* Expansion Panel */}
            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                    >
                        <div className="p-5 pt-0 border-t border-white/5">
                            <div className="pt-4 space-y-4">
                                {agent.findings && agent.findings.map((f, i) => (
                                    <div key={i} className="space-y-2 p-3 rounded-lg bg-black/20 border border-white/5">
                                        <div className="flex justify-between items-center text-[10px] font-mono text-muted mb-1">
                                            <span className="text-secondary uppercase">{f.type || 'Detection'}</span>
                                            <span>{f.filename}:{f.line_number}</span>
                                        </div>
                                        <p className="text-xs text-text-secondary leading-relaxed">
                                            {f.description}
                                        </p>
                                        {f.code && (
                                            <div className="mt-2 rounded border border-white/5 overflow-hidden">
                                                <SyntaxHighlighter
                                                    language="javascript"
                                                    style={vscDarkPlus}
                                                    customStyle={{
                                                        margin: 0,
                                                        padding: '0.75rem',
                                                        fontSize: '0.7rem',
                                                        background: '#0a0c10'
                                                    }}
                                                >
                                                    {f.code}
                                                </SyntaxHighlighter>
                                            </div>
                                        )}
                                    </div>
                                ))}

                                {!agent.findings || agent.findings.length === 0 && (
                                    <div className="flex items-start gap-3 text-xs text-text-secondary">
                                        <span className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${config.fill}`} />
                                        <p className="leading-relaxed">
                                            Summary verdict: {agent.summary}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default AgentCard;
