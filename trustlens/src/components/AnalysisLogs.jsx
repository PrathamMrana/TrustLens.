import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, CheckCircle2, Info, AlertCircle } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';

const AnalysisLogs = () => {
    const { logs } = useAnalysis();
    const scrollRef = useRef(null);

    // Auto-scroll to top (since we display newest first, or bottom if standard log style)
    // Actually, design request says "cards format", implying a list.
    // Let's show newest at the top for better visibility without scrolling.

    return (
        <div className="h-full flex flex-col bg-slate-900/50 backdrop-blur-sm border border-white/5 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5">
                <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-blue-400" />
                    Live Analysis Logs
                </h3>
                <span className="text-xs text-slate-500 font-mono">
                    {logs.length} events
                </span>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                <AnimatePresence initial={false}>
                    {logs.map((log) => (
                        <motion.div
                            key={log.id}
                            initial={{ opacity: 0, x: 20, height: 0 }}
                            animate={{ opacity: 1, x: 0, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3 }}
                            className="flex gap-3 p-3 rounded-lg bg-slate-800/50 border border-white/5 shadow-sm"
                        >
                            <div className="mt-0.5 shrink-0">
                                {log.type === 'success' ? (
                                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                ) : log.type === 'error' ? (
                                    <AlertCircle className="w-4 h-4 text-red-400" />
                                ) : (
                                    <Info className="w-4 h-4 text-blue-400" />
                                )}
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm text-slate-200 font-medium leading-relaxed">
                                    {log.message}
                                </p>
                                <p className="text-[10px] text-slate-500 font-mono mt-1">
                                    {log.timestamp}
                                </p>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {logs.length === 0 && (
                    <div className="text-center py-10 text-slate-500 text-sm">
                        Waiting for analysis to start...
                    </div>
                )}
            </div>
        </div>
    );
};

export default AnalysisLogs;
