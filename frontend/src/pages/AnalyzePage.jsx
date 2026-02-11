import React, { useState } from 'react';
import InputPanel from '../components/InputPanel';
import { useNavigate } from 'react-router-dom';
import { Shield, Zap, Brain, Search, GitMerge, CheckCircle2 } from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';
import { useAnalysis } from '../context/AnalysisContext';

const ANALYSIS_MODES = [
    {
        id: 'deep',
        title: 'Deep Analysis',
        description: 'Full multi-agent review using all 4 expert agents plus decision synthesis. Best for production code.',
        agents: [
            { name: 'Security', icon: Shield, color: 'text-red-400' },
            { name: 'Logic', icon: Brain, color: 'text-emerald-400' },
            { name: 'Quality', icon: Search, color: 'text-yellow-400' },
            { name: 'Feature', icon: Zap, color: 'text-blue-400' },
        ],
        borderColor: 'border-blue-500/20',
        bgColor: 'bg-blue-500/5',
        activeColor: 'border-blue-500/50 bg-blue-500/10 shadow-[0_0_20px_rgba(59,130,246,0.15)]',
    },
    {
        id: 'quick',
        title: 'Quick Scan',
        description: 'Fast feature extraction and quality check. Ideal for rapid feedback on small changesets.',
        agents: [
            { name: 'Feature', icon: Zap, color: 'text-blue-400' },
            { name: 'Quality', icon: Search, color: 'text-yellow-400' },
        ],
        borderColor: 'border-emerald-500/20',
        bgColor: 'bg-emerald-500/5',
        activeColor: 'border-emerald-500/50 bg-emerald-500/10 shadow-[0_0_20px_rgba(34,197,94,0.15)]',
    }
];

const AnalyzePage = () => {
    const { startAnalysis } = useAnalysis();
    const navigate = useNavigate();
    const [analysisType, setAnalysisType] = useState('deep');
    const [allowSuggestions, setAllowSuggestions] = useState(false);

    const handleStart = (input) => {
        startAnalysis(input, analysisType, allowSuggestions);
        navigate('/session/new');
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="max-w-2xl mx-auto py-12">
                <div className="text-center mb-10">
                    <h2 className="text-3xl font-bold text-white mb-3">Begin Code Analysis</h2>
                    <p className="text-slate-400">Choose your analysis mode and provide the code to review.</p>
                </div>

                {/* Analysis Mode Selector */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8"
                >
                    {ANALYSIS_MODES.map((mode) => {
                        const isActive = analysisType === mode.id;
                        return (
                            <button
                                key={mode.id}
                                onClick={() => setAnalysisType(mode.id)}
                                className={clsx(
                                    "relative p-5 rounded-xl border text-left transition-all duration-300 cursor-pointer group",
                                    isActive
                                        ? mode.activeColor
                                        : `${mode.borderColor} ${mode.bgColor} hover:border-white/20`
                                )}
                            >
                                {/* Active indicator */}
                                {isActive && (
                                    <motion.div
                                        layoutId="active-mode"
                                        className="absolute top-3 right-3"
                                    >
                                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                    </motion.div>
                                )}

                                <h3 className="text-sm font-bold text-white mb-1.5">{mode.title}</h3>
                                <p className="text-xs text-slate-400 leading-relaxed mb-4">{mode.description}</p>

                                {/* Agent Badges */}
                                <div className="flex items-center gap-2">
                                    <span className="text-[10px] uppercase text-slate-500 font-bold tracking-wider">Agents:</span>
                                    <div className="flex items-center gap-1.5">
                                        {mode.agents.map((agent) => (
                                            <div key={agent.name} className="flex items-center gap-1 px-1.5 py-0.5 bg-slate-800/60 rounded border border-slate-700/50">
                                                <agent.icon className={`w-3 h-3 ${agent.color}`} />
                                                <span className="text-[10px] text-slate-300">{agent.name}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </motion.div>

                <InputPanel onStartAnalysis={handleStart} isAnalyzing={false} />
            </div>
        </div>
    );
};

export default AnalyzePage;
