import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Brain, Zap, Search, Activity, Gauge, Lock, Eye, Code2, GitMerge, ChevronDown, ChevronRight, Cpu, Layers, ArrowRight, Database, Bot } from 'lucide-react';

const AGENT_CATALOG = [
    {
        name: "Security Analysis Agent",
        role: "Vulnerability Scanner",
        icon: Shield,
        color: "text-red-400",
        bgColor: "bg-red-500/10",
        borderColor: "border-red-500/20",
        accentGlow: "shadow-[0_0_30px_rgba(239,68,68,0.1)]",
        description: "Detects security vulnerabilities using Gemini LLM. Receives only curated features and bounded code snippets — never full files or direct S3 access.",
        capabilities: ["SQL Injection", "Auth Bypass", "Input Validation", "Crypto Weakness", "Code Execution"],
        usesLLM: true,
        dataFlow: {
            receives: "Structured features + max 5 security snippets (≤500 chars each)",
            mustNotReceive: "Full files, direct S3 access",
            outputs: "Findings with severity, confidence score, risk level"
        },
        constraints: [
            "Max 5 code snippets per analysis",
            "Max 500 characters per snippet",
            "Snippets include source → sink patterns",
            "No direct S3 access — receives pre-routed data"
        ]
    },
    {
        name: "Logic Analysis Agent",
        role: "Correctness Validator",
        icon: Brain,
        color: "text-emerald-400",
        bgColor: "bg-emerald-500/10",
        borderColor: "border-emerald-500/20",
        accentGlow: "shadow-[0_0_30px_rgba(34,197,94,0.1)]",
        description: "Analyzes code logic and correctness using Gemini LLM. Receives only logic-relevant snippets — explicitly forbidden from receiving any security-related code.",
        capabilities: ["Infinite Loops", "Unreachable Code", "Off-by-One Errors", "Logic Contradictions", "Missing Edge Cases"],
        usesLLM: true,
        dataFlow: {
            receives: "Curated logic features + max 5 logic-heavy snippets",
            mustNotReceive: "Security code (SQL, auth, crypto)",
            outputs: "Logic findings with confidence, risk level mapped from issue severity"
        },
        constraints: [
            "Max 5 logic-relevant snippets",
            "Only loops, conditionals, deeply nested code",
            "MUST NOT receive security code (SQL, auth, crypto)",
            "No direct S3 access"
        ]
    },
    {
        name: "Code Quality Agent",
        role: "Maintainability Expert",
        icon: Search,
        color: "text-yellow-400",
        bgColor: "bg-yellow-500/10",
        borderColor: "border-yellow-500/20",
        accentGlow: "shadow-[0_0_30px_rgba(245,158,11,0.1)]",
        description: "Evaluates code quality using metrics only — no raw code, no snippets, no LLM. Purely deterministic, advisory, and non-blocking.",
        capabilities: ["File Length Analysis", "Nesting Depth", "Comment Ratio", "Complexity Score", "Function Length"],
        usesLLM: false,
        dataFlow: {
            receives: "Quality metrics only (LOC, nesting, comment ratios)",
            mustNotReceive: "Raw code, code snippets",
            outputs: "Advisory findings — never blocks the pipeline"
        },
        constraints: [
            "Receives METRICS ONLY — no raw code",
            "No LLM usage — fully deterministic",
            "Advisory only — does not block decisions",
            "No S3 access"
        ]
    },
    {
        name: "Feature Extraction Agent",
        role: "Pattern Recognizer",
        icon: Zap,
        color: "text-blue-400",
        bgColor: "bg-blue-500/10",
        borderColor: "border-blue-500/20",
        accentGlow: "shadow-[0_0_30px_rgba(59,130,246,0.1)]",
        description: "Extracts static features from the full codebase without using LLM. This is the ONLY agent allowed to scan the entire codebase — all other agents receive pre-routed data.",
        capabilities: ["Language Detection", "LoC Counting", "Nesting Analysis", "Function/Class Counting", "File Size Metrics"],
        usesLLM: false,
        dataFlow: {
            receives: "Full codebase from orchestrator",
            mustNotReceive: "N/A — this is the source agent",
            outputs: "Structured features used by all downstream agents"
        },
        constraints: [
            "ONLY agent allowed to scan full codebase",
            "Outputs structured features only",
            "No LLM — purely static analysis",
            "Deterministic (confidence always 1.0)"
        ]
    },
    {
        name: "Decision Agent",
        role: "Consensus Synthesizer",
        icon: GitMerge,
        color: "text-purple-400",
        bgColor: "bg-purple-500/10",
        borderColor: "border-purple-500/20",
        accentGlow: "shadow-[0_0_30px_rgba(139,92,246,0.1)]",
        description: "Synthesizes findings from all expert agents into a unified recommendation. Maps the highest risk level to an action and applies conflict penalties to confidence scores.",
        capabilities: ["Risk Synthesis", "Action Recommendation", "Conflict Penalty", "Agent Trace Storage", "Decision Confidence"],
        usesLLM: false,
        dataFlow: {
            receives: "All agent outputs, overall confidence, conflict list",
            mustNotReceive: "Raw code — operates on agent outputs only",
            outputs: "Final recommendation: acceptable / proceed_with_caution / review_required / manual_review_required"
        },
        constraints: [
            "Maps highest risk → recommended action",
            "Applies 20% penalty per conflict (capped at 50%)",
            "Stores full agent traces for explainability",
            "Does not analyze code directly"
        ]
    }
];

const PIPELINE_STEPS = [
    { label: "Code Input", icon: Code2, color: "text-blue-400", description: "Repo URL or snippet" },
    { label: "Feature Agent", icon: Zap, color: "text-blue-400", description: "Static analysis of full codebase" },
    { label: "Routing Policy", icon: Layers, color: "text-cyan-400", description: "Curates data per agent" },
    { label: "Expert Agents", icon: Bot, color: "text-amber-400", description: "Security · Logic · Quality", isGroup: true },
    { label: "Decision Agent", icon: GitMerge, color: "text-purple-400", description: "Synthesizes consensus" },
    { label: "Final Report", icon: Database, color: "text-emerald-400", description: "Explainable verdict" },
];

const AgentDeepDive = ({ agent }) => {
    return (
        <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
        >
            <div className="mt-4 pt-4 border-t border-white/5 space-y-4">
                {/* Data Flow */}
                <div className="space-y-3">
                    <h5 className="text-[10px] uppercase tracking-widest text-slate-500 font-bold flex items-center gap-1.5">
                        <ArrowRight className="w-3 h-3" /> Data Flow
                    </h5>
                    <div className="grid grid-cols-1 gap-2">
                        <div className="px-3 py-2 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                            <span className="text-[10px] uppercase text-emerald-500 font-bold">Receives</span>
                            <p className="text-xs text-slate-300 mt-0.5">{agent.dataFlow.receives}</p>
                        </div>
                        <div className="px-3 py-2 rounded-lg bg-red-500/5 border border-red-500/10">
                            <span className="text-[10px] uppercase text-red-400 font-bold">Must Not Receive</span>
                            <p className="text-xs text-slate-300 mt-0.5">{agent.dataFlow.mustNotReceive}</p>
                        </div>
                        <div className="px-3 py-2 rounded-lg bg-blue-500/5 border border-blue-500/10">
                            <span className="text-[10px] uppercase text-blue-400 font-bold">Outputs</span>
                            <p className="text-xs text-slate-300 mt-0.5">{agent.dataFlow.outputs}</p>
                        </div>
                    </div>
                </div>

                {/* Constraints */}
                <div className="space-y-2">
                    <h5 className="text-[10px] uppercase tracking-widest text-slate-500 font-bold flex items-center gap-1.5">
                        <Lock className="w-3 h-3" /> PRD Constraints
                    </h5>
                    <div className="space-y-1.5">
                        {agent.constraints.map((c, i) => (
                            <div key={i} className="flex items-start gap-2 text-xs text-slate-400">
                                <span className={`w-1 h-1 rounded-full mt-1.5 flex-shrink-0 ${agent.bgColor.replace('/10', '')}`} />
                                {c}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

const AgentsPage = () => {
    const [expandedAgent, setExpandedAgent] = useState(null);

    return (
        <div className="max-w-6xl mx-auto py-12 px-4">
            {/* Header */}
            <div className="mb-12">
                <h1 className="text-3xl font-bold text-white mb-3">Agent Orchestration</h1>
                <p className="text-slate-400 max-w-2xl">
                    TrustLens deploys a specialized ensemble of 5 AI agents. Each agent operates independently with strict data boundaries before their findings are synthesized by the Decision Agent.
                </p>
            </div>

            {/* Architecture Pipeline */}
            <div className="mb-12 p-6 rounded-xl border border-white/5 bg-slate-900/30 backdrop-blur-sm">
                <h2 className="text-xs uppercase tracking-widest text-slate-500 font-bold mb-6 flex items-center gap-2">
                    <Cpu className="w-3.5 h-3.5" /> Agent Architecture Pipeline
                </h2>
                <div className="flex flex-wrap items-center justify-center gap-2 md:gap-0">
                    {PIPELINE_STEPS.map((step, idx) => (
                        <React.Fragment key={step.label}>
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                className={`flex flex-col items-center text-center px-3 py-3 rounded-lg border ${step.isGroup ? 'border-amber-500/20 bg-amber-500/5' : 'border-white/5 bg-white/[0.02]'} min-w-[100px] hover:bg-white/5 transition-colors`}
                            >
                                <step.icon className={`w-5 h-5 ${step.color} mb-1.5`} />
                                <span className="text-xs font-semibold text-white">{step.label}</span>
                                <span className="text-[10px] text-slate-500 mt-0.5">{step.description}</span>
                            </motion.div>
                            {idx < PIPELINE_STEPS.length - 1 && (
                                <div className="hidden md:flex items-center px-1">
                                    <ArrowRight className="w-4 h-4 text-slate-600" />
                                </div>
                            )}
                        </React.Fragment>
                    ))}
                </div>
            </div>

            {/* Agent Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {AGENT_CATALOG.map((agent, idx) => {
                    const isExpanded = expandedAgent === agent.name;
                    return (
                        <motion.div
                            key={agent.name}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.08 }}
                            className={`p-6 rounded-xl border ${agent.borderColor} ${agent.bgColor} backdrop-blur-sm transition-all duration-300 hover:${agent.accentGlow}`}
                        >
                            {/* Header Row */}
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className={`p-3 rounded-lg ${agent.bgColor} border ${agent.borderColor}`}>
                                        <agent.icon className={`w-6 h-6 ${agent.color}`} />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                                        <p className="text-xs uppercase tracking-wider opacity-70 font-mono text-slate-400">{agent.role}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    {agent.usesLLM ? (
                                        <span className="px-2 py-0.5 rounded text-[9px] font-bold uppercase bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                            LLM
                                        </span>
                                    ) : (
                                        <span className="px-2 py-0.5 rounded text-[9px] font-bold uppercase bg-slate-500/10 text-slate-400 border border-slate-500/20">
                                            Deterministic
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Description */}
                            <p className="text-slate-300 text-sm leading-relaxed mb-5">
                                {agent.description}
                            </p>

                            {/* Capabilities */}
                            <div className="mb-4">
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

                            {/* Expand/Collapse */}
                            <button
                                onClick={() => setExpandedAgent(isExpanded ? null : agent.name)}
                                className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors mt-2 cursor-pointer"
                            >
                                <Eye className="w-3 h-3" />
                                {isExpanded ? 'Hide' : 'View'} Data Flow & Constraints
                                {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                            </button>

                            {/* Deep Dive Panel */}
                            <AnimatePresence>
                                {isExpanded && <AgentDeepDive agent={agent} />}
                            </AnimatePresence>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
};

export default AgentsPage;
