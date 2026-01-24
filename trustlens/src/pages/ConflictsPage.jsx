import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, ShieldAlert, GitMerge, Check, X } from 'lucide-react';
import ConflictPanel from '../components/ConflictPanel';

const ConflictsPage = () => {
    return (
        <div className="max-w-5xl mx-auto py-12">
            <div className="mb-12">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs font-mono mb-4">
                    <ShieldAlert className="w-3 h-3" />
                    <span>ACTIVE DISPUTE DETECTED</span>
                </div>
                <h1 className="text-3xl font-bold text-white mb-3">Conflict Resolution Center</h1>
                <p className="text-slate-400 max-w-2xl">
                    When autonomous agents reach differing conclusions, the system elevates the decision to this panel.
                    TrustLens refuses to suppress ambiguity, ensuring human reviewers see the full context of the disagreement.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Conflict Detail - Left Column */}
                <div className="lg:col-span-2 space-y-6">
                    <ConflictPanel conflict={true} />

                    <div className="p-6 rounded-xl border border-white/5 bg-slate-900/50">
                        <h3 className="text-sm font-semibold text-slate-300 mb-6 flex items-center gap-2">
                            <GitMerge className="w-4 h-4 text-purple-400" /> Divergence Analysis
                        </h3>

                        <div className="relative pl-6 border-l border-slate-700 space-y-8">
                            {/* Security Agent View */}
                            <div className="relative">
                                <div className="absolute -left-[29px] top-0 w-3 h-3 rounded-full bg-red-500 border-2 border-slate-900" />
                                <h4 className="text-red-400 font-medium text-sm mb-2">Security Agent Perspective</h4>
                                <div className="bg-red-500/5 p-4 rounded-lg border border-red-500/10 text-sm text-slate-300 leading-relaxed">
                                    "The pattern at `lines 45-48` resembles a raw SQL concatenation. Although the variable names suggest sanitization, there is no explicit typesafe binding found in the call graph."
                                </div>
                            </div>

                            {/* Logic Agent View */}
                            <div className="relative">
                                <div className="absolute -left-[29px] top-0 w-3 h-3 rounded-full bg-emerald-500 border-2 border-slate-900" />
                                <h4 className="text-emerald-400 font-medium text-sm mb-2">Logic Agent Perspective</h4>
                                <div className="bg-emerald-500/5 p-4 rounded-lg border border-emerald-500/10 text-sm text-slate-300 leading-relaxed">
                                    "The control flow for `processUserData` is valid. All paths return a deterministic boolean result. No unreachable states detected."
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Sidebar - Resolution Actions */}
                <div className="space-y-6">
                    <div className="p-5 rounded-xl border border-white/5 bg-slate-900/50">
                        <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-4">Manual Override</h4>
                        <p className="text-xs text-slate-400 mb-4">
                            As a senior reviewer, you may resolve this conflict by accepting one of the agent's verdicts.
                        </p>
                        <div className="space-y-3">
                            <button className="w-full flex items-center justify-between p-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 hover:bg-emerald-500/10 text-emerald-400 text-sm transition-colors">
                                <span>Accept Logic (Safe)</span>
                                <Check className="w-4 h-4" />
                            </button>
                            <button className="w-full flex items-center justify-between p-3 rounded-lg border border-red-500/20 bg-red-500/5 hover:bg-red-500/10 text-red-400 text-sm transition-colors">
                                <span>Confirm Risk</span>
                                <AlertTriangle className="w-4 h-4" />
                            </button>
                            <button className="w-full flex items-center justify-between p-3 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition-colors">
                                <span>Dismiss (False Positive)</span>
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ConflictsPage;
