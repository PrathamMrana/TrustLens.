import { useAnalysis } from '../context/AnalysisContext';
import { FileText, Download, Share2, Shield, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

const ReportPage = () => {
    const { report, results, status, analysisId } = useAnalysis();

    if (status === 'IDLE') return <div className="text-center py-20 text-slate-400">No report available. Start an analysis first.</div>;
    if (status === 'ANALYZING' || status === 'UPLOADING') return <div className="text-center py-20 text-slate-400">Analysis in progress...</div>;
    if (!report) return <div className="text-center py-20 text-slate-400">Report data not found.</div>;

    const formattedDate = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });

    return (
        <div className="max-w-4xl mx-auto py-12">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-2">Audit Report #{analysisId?.substring(0, 8).toUpperCase()}</h1>
                    <p className="text-slate-400 text-sm">Generated on {formattedDate} • UTC</p>
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
                        <div className={`px-3 py-1 rounded text-sm font-medium border ${report.deferred
                                ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-500"
                                : "bg-emerald-500/10 border-emerald-500/20 text-emerald-500"
                            }`}>
                            {report.final_decision?.toUpperCase()}
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="p-8 space-y-8">
                    <div>
                        <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-4">Evaluation Context</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="p-4 rounded-lg bg-slate-900/50 border border-white/5">
                                <div className="text-slate-500 text-xs mb-1">Target</div>
                                <div className="text-slate-300 text-sm font-mono truncate">{report.repository_url || "Uploaded Source"}</div>
                            </div>
                            <div className="p-4 rounded-lg bg-slate-900/50 border border-white/5">
                                <div className="text-slate-500 text-xs mb-1">Risk Level</div>
                                <div className={`text-sm font-bold ${report.overall_risk_level === 'high' || report.overall_risk_level === 'critical'
                                        ? 'text-red-400' : report.overall_risk_level === 'medium' ? 'text-yellow-400' : 'text-emerald-400'
                                    }`}>
                                    {report.overall_risk_level?.toUpperCase()}
                                </div>
                            </div>
                            <div className="p-4 rounded-lg bg-slate-900/50 border border-white/5">
                                <div className="text-slate-500 text-xs mb-1">Confidence</div>
                                <div className="text-slate-300 text-sm">{Math.round(report.overall_confidence * 100)}%</div>
                            </div>
                            <div className="p-4 rounded-lg bg-slate-900/50 border border-white/5">
                                <div className="text-slate-500 text-xs mb-1">Consensus</div>
                                <div className="text-slate-300 text-sm">{report.disagreement_detected ? "Disputed" : "Unified"}</div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-4">Reasoning</h4>
                        <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20">
                            <p className="text-slate-300 text-sm leading-relaxed italic">
                                "{report.system_reasoning}"
                                {report.deferred && (
                                    <span className="block mt-2 text-yellow-500/80 not-italic font-medium">
                                        Reason for Deferral: {report.deferral_reason}
                                    </span>
                                )}
                            </p>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-4">Agent Verdicts</h4>
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
                                    {results && results.map((res, i) => (
                                        <tr key={i}>
                                            <td className="p-4 flex items-center gap-2">
                                                {res.name.includes('Security') ? <Shield className="w-4 h-4 text-red-400" /> :
                                                    res.name.includes('Logic') ? <Brain className="w-4 h-4 text-emerald-400" /> :
                                                        <Activity className="w-4 h-4 text-blue-400" />} {res.name}
                                            </td>
                                            <td className={`p-4 font-medium ${res.risk === 'high' || res.risk === 'critical' ? 'text-red-400' :
                                                    res.risk === 'medium' ? 'text-yellow-400' : 'text-emerald-400'
                                                }`}>
                                                {res.risk?.toUpperCase()}
                                            </td>
                                            <td className="p-4">{res.confidence}%</td>
                                            <td className="p-4 max-w-xs truncate">{res.summary}</td>
                                        </tr>
                                    ))}
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
