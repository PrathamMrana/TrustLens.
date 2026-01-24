import React, { useState } from 'react';
import InputPanel from '../components/InputPanel';
import { useSimulation } from '../context/SimulationContext';
import { useNavigate } from 'react-router-dom';
import { Shield, Zap, Info } from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

const AnalyzePage = () => {
    const { startAnalysis } = useSimulation();
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
                    <p className="text-slate-400">Configure your analysis parameters.</p>
                </div>

                <InputPanel onStartAnalysis={handleStart} isAnalyzing={false} />

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6 w-full px-4"
                >
                    {/* Analysis Mode Selection */}
                    <div className="p-5 rounded-xl border border-white/5 bg-slate-900/50 backdrop-blur-sm">
                        <h4 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                            <Shield className="w-4 h-4 text-blue-400" /> Analysis Depth
                        </h4>
                        <div className="space-y-3">
                            <label className={clsx(
                                "flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all",
                                analysisType === 'quick'
                                    ? "bg-blue-500/10 border-blue-500/50 text-white"
                                    : "border-slate-800 hover:bg-slate-800/50 text-slate-400"
                            )}>
                                <input
                                    type="radio"
                                    name="mode"
                                    value="quick"
                                    checked={analysisType === 'quick'}
                                    onChange={(e) => setAnalysisType(e.target.value)}
                                    className="hidden"
                                />
                                <Zap className="w-4 h-4" />
                                <div className="flex-1">
                                    <div className="font-medium text-sm">Quick Scan</div>
                                    <div className="text-xs opacity-70">Heuristic-based (Faster)</div>
                                </div>
                            </label>

                            <label className={clsx(
                                "flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all",
                                analysisType === 'deep'
                                    ? "bg-blue-500/10 border-blue-500/50 text-white"
                                    : "border-slate-800 hover:bg-slate-800/50 text-slate-400"
                            )}>
                                <input
                                    type="radio"
                                    name="mode"
                                    value="deep"
                                    checked={analysisType === 'deep'}
                                    onChange={(e) => setAnalysisType(e.target.value)}
                                    className="hidden"
                                />
                                <Shield className="w-4 h-4" />
                                <div className="flex-1">
                                    <div className="font-medium text-sm">Deep Review</div>
                                    <div className="text-xs opacity-70">Semantic Analysis (Recommended)</div>
                                </div>
                            </label>
                        </div>
                    </div>

                    {/* AI Suggestions Toggle */}
                    <div className="p-5 rounded-xl border border-white/5 bg-slate-900/50 backdrop-blur-sm">
                        <h4 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                            <Info className="w-4 h-4 text-purple-400" /> Optional Features
                        </h4>

                        <label className="flex items-start gap-3 p-3 rounded-lg border border-slate-800 hover:bg-slate-800/50 cursor-pointer transition-colors">
                            <div className="relative flex items-center mt-1">
                                <input
                                    type="checkbox"
                                    checked={allowSuggestions}
                                    onChange={(e) => setAllowSuggestions(e.target.checked)}
                                    className="peer sr-only"
                                />
                                <div className="w-9 h-5 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                            </div>
                            <div>
                                <div className="font-medium text-sm text-slate-200">Allow AI Suggestions</div>
                                <p className="text-xs text-slate-500 mt-1">
                                    Enable experimental auto-fix suggestions.
                                    <span className="text-yellow-500 block mt-1">⚠️ Use with caution (Beta)</span>
                                </p>
                            </div>
                        </label>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default AnalyzePage;
