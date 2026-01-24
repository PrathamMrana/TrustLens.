import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Brain, Zap, Search, Activity, Gauge } from 'lucide-react';

const AGENT_CATALOG = [
    {
        name: "Security Agent",
        role: "Vulnerability Scanner",
        icon: Shield,
        color: "text-red-400 bg-red-500/10 border-red-500/20",
        description: "Specializes in identifying OWASP Top 10 vulnerabilities, injection flaws, and insecure configurations. Trained on common CVE patterns.",
        capabilities: ["SQL Injection", "XSS", "Insecure Deserialization", "Auth Bypass"],
        calibration: "Optimized for high recall to prevent false negatives."
    },
    {
        name: "Logic Agent",
        role: "Correctness Validator",
        icon: Brain,
        color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        description: "Analyzes control flow graphs to detect unreachable code, infinite loops, and logical contradictions. Semantic understanding of business constraints.",
        capabilities: ["Dead Code", "Infinite Loops", "Race Conditions", "Type Inconsistencies"],
        calibration: "Balanced precision and recall."
    },
    {
        name: "Quality Agent",
        role: "Maintainability Expert",
        icon: Search,
        color: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
        description: "Evaluates code complexity, cognitive load, and adherence to style guides. Flags 'smells' that impede long-term maintenance.",
        capabilities: ["Cyclomatic Complexity", "Cognitive Complexity", "Code Duplication", "Naming Conventions"],
        calibration: "Tunable strictness based on project settings."
    },
    {
        name: "Feature Agent",
        role: "Pattern Recognizer",
        icon: Zap,
        color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
        description: "Identifies architectural patterns and high-level feature implementations. Provides context for other agents.",
        capabilities: ["Architectural Patterns", "API Endpoints", "Database Models", "Auth Flows"],
        calibration: "High precision for architectural identification."
    }
];

const AgentsPage = () => {
    return (
        <div className="max-w-6xl mx-auto py-12">
            <div className="mb-12">
                <h1 className="text-3xl font-bold text-white mb-3">Agent Orchestration</h1>
                <p className="text-slate-400 max-w-2xl">
                    TrustLens deploys a specialized ensemble of AI agents. Each agent operates independently before their findings are synthesized by the central Orchestrator.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {AGENT_CATALOG.map((agent, idx) => (
                    <motion.div
                        key={agent.name}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className={`p-6 rounded-xl border ${agent.color} backdrop-blur-sm`}
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className={`p-3 rounded-lg ${agent.color.replace('border-', '')}`}>
                                    <agent.icon className="w-6 h-6" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                                    <p className="text-xs uppercase tracking-wider opacity-70 font-mono">{agent.role}</p>
                                </div>
                            </div>
                            <div className="p-2 rounded-full bg-slate-900/50">
                                <Activity className="w-4 h-4 text-slate-500" />
                            </div>
                        </div>

                        <p className="text-slate-300 text-sm leading-relaxed mb-6">
                            {agent.description}
                        </p>

                        <div>
                            <h4 className="text-xs text-slate-500 uppercase font-bold mb-3 flex items-center gap-2">
                                <Gauge className="w-3 h-3" /> Core Capabilities
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {agent.capabilities.map(cap => (
                                    <span key={cap} className="px-2 py-1 bg-slate-800/50 rounded border border-slate-700 text-xs text-slate-300">
                                        {cap}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

export default AgentsPage;
