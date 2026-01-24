import React from 'react';
import { History, ArrowRight, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const MOCK_HISTORY = [
    { id: "TR-8829", date: "Jan 24, 14:32", repo: "auth-service", status: "Manual Review", risk: "high" },
    { id: "TR-8810", date: "Jan 23, 09:15", repo: "payment-gateway", status: "Safe", risk: "low" },
    { id: "TR-8755", date: "Jan 22, 18:45", repo: "frontend-ui", status: "Safe", risk: "low" },
    { id: "TR-8721", date: "Jan 21, 11:20", repo: "legacy-api", status: "High Risk", risk: "high" },
];

const HistoryPage = () => {
    return (
        <div className="max-w-4xl mx-auto py-12">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-white mb-2">Analysis History</h1>
                <p className="text-slate-400">Archive of all past code review sessions.</p>
            </div>

            <div className="bg-surface border border-white/5 rounded-xl overflow-hidden">
                <div className="space-y-1">
                    {MOCK_HISTORY.map((item) => (
                        <div key={item.id} className="p-4 hover:bg-white/5 transition-colors flex items-center justify-between group cursor-pointer border-b border-white/5 last:border-0">
                            <div className="flex items-center gap-4">
                                <div className={`p-2 rounded-lg ${item.risk === 'high' ? 'bg-red-500/10 text-red-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
                                    {item.risk === 'high' ? <ShieldAlert className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
                                </div>
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-white font-medium">{item.repo}</span>
                                        <span className="text-xs text-slate-500 font-mono">#{item.id}</span>
                                    </div>
                                    <div className="text-xs text-slate-400 mt-1">{item.date} • {item.status}</div>
                                </div>
                            </div>

                            <Link to={`/report`} className="flex items-center gap-2 text-sm text-slate-500 group-hover:text-blue-400 transition-colors">
                                View Report <ArrowRight className="w-4 h-4" />
                            </Link>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default HistoryPage;
