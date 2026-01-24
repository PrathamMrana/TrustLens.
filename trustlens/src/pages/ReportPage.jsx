import React from 'react';
import { MOCK_RESULTS } from '../context/SimulationContext'; // We might need to export this or just mock again
import { FileText, Download, Share2, Shield, CheckCircle2 } from 'lucide-react';

const ReportPage = () => {
    return (
        <div className="max-w-4xl mx-auto py-12">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-2">Audit Report #TR-8829</h1>
                    <p className="text-slate-400 text-sm">Generated on Jan 24, 2026 • 14:32:01 UTC</p>
                </div>
                <div className="flex gap-3">
                    <button className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 text-sm transition-colors">
                        <Share2 className="w-4 h-4" /> Share
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm transition-colors shadow-lg shadow-blue-500/20">
                        <Download className="w-4 h-4" /> Export PDF
                    </button>
                </div>
            </div>

            <div className="bg-white/5 border border-white/5 rounded-2xl overflow-hidden backdrop-blur-md">
                {/* Header */}
                <div className="p-8 border-b border-white/5 bg-white/5">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-lg font-semibold text-white">Executive Summary</h3>
                            <p className="text-slate-400 text-sm mt-1">Multi-Agent Consensus Analysis</p>
                        </div>
                        <div className="px-3 py-1 bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 rounded text-sm font-medium">
                            MANUAL REVIEW REQUIRED
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="p-8 space-y-8">
                    <div>
                        <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-4">Evaluation Context</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="p-4 rounded-lg bg-slate-900/50 border border-white/5">
                                <div className="text-slate-500 text-xs mb-1">Target Repository</div>
                                <div className="text-slate-300 text-sm font-mono truncate">github.com/corp/auth-svc</div>
                            </div>
                            <div className="p-4 rounded-lg bg-slate-900/50 border border-white/5">
                                <div className="text-slate-500 text-xs mb-1">Analysis Mode</div>
                                <div className="text-slate-300 text-sm">Deep Review</div>
                            </div>
                            <div className="p-4 rounded-lg bg-slate-900/50 border border-white/5">
                                <div className="text-slate-500 text-xs mb-1">Total Agents</div>
                                <div className="text-slate-300 text-sm">4 Active</div>
                            </div>
                            <div className="p-4 rounded-lg bg-slate-900/50 border border-white/5">
                                <div className="text-slate-500 text-xs mb-1">Risk Score</div>
                                <div className="text-yellow-400 text-sm">Elevated</div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-4">Detailed Verdicts</h4>
                        <div className="border border-white/5 rounded-lg overflow-hidden">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-slate-900/50 text-slate-400 font-medium">
                                    <tr>
                                        <th className="p-4">Agent</th>
                                        <th className="p-4">Risk Level</th>
                                        <th className="p-4">Confidence</th>
                                        <th className="p-4">Primary Finding</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5 text-slate-300">
                                    <tr>
                                        <td className="p-4 flex items-center gap-2">
                                            <Shield className="w-4 h-4 text-red-400" /> Security
                                        </td>
                                        <td className="p-4 text-red-400">High</td>
                                        <td className="p-4">88%</td>
                                        <td className="p-4">Auth Injection Risk</td>
                                    </tr>
                                    <tr>
                                        <td className="p-4 flex items-center gap-2">
                                            <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Logic
                                        </td>
                                        <td className="p-4 text-emerald-400">Low</td>
                                        <td className="p-4">94%</td>
                                        <td className="p-4">Valid Control Flow</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReportPage;
