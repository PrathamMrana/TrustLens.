import React from 'react';
import { useAnalysis } from '../context/AnalysisContext';
import { FileText, Download, Share2, Shield, CheckCircle2, AlertTriangle, Info, Brain, Activity, Code2, Globe, Layers, Cpu } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

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
        <div className="max-w-4xl mx-auto py-12 px-4">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-2">Audit Report #{analysisId?.substring(0, 8).toUpperCase()}</h1>
                    <p className="text-slate-400 text-sm">Generated on {formattedDate} • UTC</p>
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
                        <div className={`px-3 py-1 rounded text-sm font-medium border ${report.final_decision === 'proceed_with_caution'
                            ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-500"
                            : report.final_decision === 'acceptable'
                                ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-500"
                                : "bg-red-500/10 border-red-500/20 text-red-500"
                            }`}>
                            {report.final_decision?.replace(/_/g, ' ').toUpperCase()}
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
                                <div className="text-slate-500 text-xs mb-1">Analysis Confidence</div>
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
                            </p>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-4">Agent Verdicts</h4>
                        <div className="border border-white/5 rounded-lg overflow-hidden mb-8">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-slate-900/50 text-slate-400 font-medium">
                                    <tr>
                                        <th className="p-4">Agent</th>
                                        <th className="p-4">Risk Level</th>
                                        <th className="p-4">Confidence</th>
                                        <th className="p-4">Summary</th>
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

                    {/* Project DNA (Feature Overview) */}
                    <div className="pt-8 border-t border-white/5">
                        <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-6">Project DNA & Architecture</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {report.quality_summary?.metrics?.languages?.map(lang => (
                                <div key={lang} className="p-6 rounded-2xl bg-blue-500/5 border border-blue-500/10 flex flex-col gap-4 relative overflow-hidden group hover:bg-blue-500/10 transition-all">
                                    <div className="flex items-center justify-between relative z-10">
                                        <Code2 className="w-6 h-6 text-blue-400" />
                                        <span className="text-[10px] font-bold text-blue-500/50 uppercase tracking-widest">Language</span>
                                    </div>
                                    <div className="relative z-10">
                                        <div className="text-2xl font-bold text-white uppercase">{lang}</div>
                                        <div className="text-xs text-slate-400 mt-1">Core implementation environment</div>
                                    </div>
                                    <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
                                        <Globe className="w-24 h-24 text-white" />
                                    </div>
                                </div>
                            ))}

                            <div className="p-6 rounded-2xl bg-purple-500/5 border border-purple-500/10 flex flex-col gap-4 relative overflow-hidden group hover:bg-purple-500/10 transition-all">
                                <div className="flex items-center justify-between relative z-10">
                                    <Layers className="w-6 h-6 text-purple-400" />
                                    <span className="text-[10px] font-bold text-purple-500/50 uppercase tracking-widest">Complexity</span>
                                </div>
                                <div className="relative z-10">
                                    <div className="text-2xl font-bold text-white max-w-[150px] truncate" title={report.quality_summary?.metrics?.max_nesting_depth || 0}>{report.quality_summary?.metrics?.max_nesting_depth || 0} Levels</div>
                                    <div className="text-xs text-slate-400 mt-1">Maximum architectural nesting</div>
                                </div>
                                <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
                                    <Cpu className="w-24 h-24 text-white" />
                                </div>
                            </div>

                            <div className="p-6 rounded-2xl bg-emerald-500/5 border border-emerald-500/10 flex flex-col gap-4 relative overflow-hidden group hover:bg-emerald-500/10 transition-all">
                                <div className="flex items-center justify-between relative z-10">
                                    <Globe className="w-6 h-6 text-emerald-400" />
                                    <span className="text-[10px] font-bold text-emerald-500/50 uppercase tracking-widest">Footprint</span>
                                </div>
                                <div className="relative z-10">
                                    <div className="text-2xl font-bold text-white">{report.quality_summary?.metrics?.total_loc || 0} LoC</div>
                                    <div className="text-xs text-slate-400 mt-1">Total active lines of source</div>
                                </div>
                                <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
                                    <Code2 className="w-24 h-24 text-white" />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Detailed Findings Section */}
                    <div className="pt-8 border-t border-white/5">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <FileText className="w-5 h-5 text-blue-400" /> Technical Deep Dive
                        </h3>

                        <div className="space-y-6">
                            {results && results.map((agent) => (
                                agent.findings && agent.findings.length > 0 && (
                                    <div key={agent.name} className="space-y-4">
                                        <h4 className="text-sm font-semibold text-slate-400 flex items-center gap-2">
                                            {agent.name} Context
                                        </h4>

                                        {agent.findings.map((finding, fidx) => (
                                            <div key={fidx} className="bg-slate-900/80 border border-white/5 rounded-xl overflow-hidden">
                                                <div className="px-4 py-3 bg-white/5 flex items-center justify-between border-b border-white/5">
                                                    <div className="flex items-center gap-3">
                                                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${finding.severity === 'critical' || finding.severity === 'high' ? 'bg-red-500/20 text-red-500' :
                                                            finding.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-500' : 'bg-blue-500/20 text-blue-500'
                                                            }`}>
                                                            {finding.severity || finding.type}
                                                        </span>
                                                        <span className="text-xs font-mono text-slate-400">
                                                            {finding.filename}:{finding.line_number}
                                                        </span>
                                                    </div>
                                                </div>

                                                <div className="p-4">
                                                    <p className="text-sm text-slate-200 mb-4">{finding.description}</p>

                                                    {finding.code && (
                                                        <div className="relative group rounded-lg overflow-hidden border border-white/5 shadow-2xl">
                                                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500/50 z-20"></div>
                                                            <SyntaxHighlighter
                                                                language={
                                                                    agent.name.toLowerCase().includes('python') ? 'python' :
                                                                        agent.name.toLowerCase().includes('java') ? 'java' :
                                                                            agent.name.toLowerCase().includes('typescript') ? 'typescript' :
                                                                                'javascript'
                                                                }
                                                                style={vscDarkPlus}
                                                                customStyle={{
                                                                    margin: 0,
                                                                    padding: '1.5rem',
                                                                    fontSize: '0.75rem',
                                                                    lineHeight: '1.6',
                                                                    background: '#0a0c10'
                                                                }}
                                                                showLineNumbers={true}
                                                            >
                                                                {finding.code}
                                                            </SyntaxHighlighter>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReportPage;
