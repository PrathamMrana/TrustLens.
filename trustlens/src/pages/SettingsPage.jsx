import React from 'react';
import { Lock, Sliders, Shield } from 'lucide-react';

const SettingsPage = () => {
    return (
        <div className="max-w-3xl mx-auto py-12">
            <h1 className="text-2xl font-bold text-white mb-8">System Configuration</h1>

            <div className="space-y-6">
                {/* Section 1: Responsible AI */}
                <div className="p-6 rounded-xl border border-blue-500/20 bg-blue-500/5">
                    <h3 className="text-md font-semibold text-blue-100 mb-4 flex items-center gap-2">
                        <Shield className="w-4 h-4" /> AI Safety Protocols
                    </h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-sm text-slate-200 font-medium">Prefer Caution Over Speed</div>
                                <div className="text-xs text-slate-400">System will deliberately slow down analysis to run deeper verification.</div>
                            </div>
                            <div className="px-3 py-1 bg-blue-500/20 text-blue-300 text-xs font-mono rounded border border-blue-500/30">LOCKED (ON)</div>
                        </div>

                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-sm text-slate-200 font-medium">Force Human Review on Conflict</div>
                                <div className="text-xs text-slate-400">If agents disagree, disallow automated approval.</div>
                            </div>
                            <div className="px-3 py-1 bg-blue-500/20 text-blue-300 text-xs font-mono rounded border border-blue-500/30">LOCKED (ON)</div>
                        </div>
                    </div>
                </div>

                {/* Section 2: Thresholds */}
                <div className="p-6 rounded-xl border border-white/5 bg-slate-900/50 opacity-70">
                    <h3 className="text-md font-semibold text-slate-300 mb-4 flex items-center gap-2">
                        <Sliders className="w-4 h-4" /> Confidence Thresholds
                    </h3>
                    <div className="space-y-6">
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-slate-400">Minimum Confidence for Auto-Approval</span>
                                <span className="text-white font-mono">98%</span>
                            </div>
                            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full w-[98%] bg-slate-600 rounded-full"></div>
                            </div>
                        </div>

                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-slate-400">Security Agent Sensitivity</span>
                                <span className="text-white font-mono">High (Paranoid)</span>
                            </div>
                            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full w-[85%] bg-slate-600 rounded-full"></div>
                            </div>
                        </div>
                    </div>
                    <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
                        <Lock className="w-3 h-3" />
                        <span>Settings are managed by your organization administrator.</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
