import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Code, ArrowRight, FileCode, CheckCircle2, Lock } from 'lucide-react';
import clsx from 'clsx';

const InputPanel = ({ onStartAnalysis, isAnalyzing }) => {
    const [input, setInput] = useState('');
    const [ingestionState, setIngestionState] = useState('idle'); // idle, focusing, ingesting, confirmed

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (input.trim()) {
            setIngestionState('ingesting');

            // 4-Stage Animation delay simulation
            // Stage 1: "Capturing..."
            await new Promise(r => setTimeout(r, 800));

            // Stage 2: "Extracting metadata..." (Internal state change could happen here)
            await new Promise(r => setTimeout(r, 800));

            // Stage 3: Confirmed
            setIngestionState('confirmed');
            await new Promise(r => setTimeout(r, 800));

            // Hand off to parent
            onStartAnalysis(input);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="w-full max-w-3xl mx-auto mt-12 mb-8"
        >
            <div className="bg-surface border border-border rounded-card p-1 shadow-soft">
                <div className="bg-background/50 rounded-lg p-6 border border-white/5 relative overflow-hidden">

                    {/* Header - Fades out during ingestion */}
                    <AnimatePresence>
                        {ingestionState === 'idle' && (
                            <motion.div
                                exit={{ opacity: 0, height: 0 }}
                                className="flex items-center gap-3 mb-4"
                            >
                                <Code className="w-5 h-5 text-brand" />
                                <h2 className="text-lg font-medium text-primary">Analysis Target</h2>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <form onSubmit={handleSubmit} className="relative group">
                        <AnimatePresence mode="wait">
                            {ingestionState === 'idle' ? (
                                <motion.div
                                    key="input-mode"
                                    exit={{ opacity: 0, y: -20 }}
                                >
                                    <textarea
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        placeholder="Paste repository URL or code snippet for verified analysis..."
                                        className="w-full bg-secondary text-primary placeholder:text-muted border border-border rounded-input min-h-[120px] p-4 focus:ring-1 focus:ring-brand/30 focus:border-brand/50 transition-all resize-none font-mono text-sm leading-relaxed outline-none"
                                    />
                                    <div className="absolute bottom-4 right-4">
                                        <button
                                            type="submit"
                                            disabled={!input.trim()}
                                            className={clsx(
                                                "flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all shadow-lg",
                                                !input.trim()
                                                    ? 'bg-secondary text-muted cursor-not-allowed border border-border'
                                                    : 'bg-brand hover:bg-blue-600 text-white shadow-blue-500/20'
                                            )}
                                        >
                                            Start Analysis <ArrowRight className="w-4 h-4" />
                                        </button>
                                    </div>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="ingestion-mode"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="min-h-[120px] flex flex-col items-center justify-center text-center py-4"
                                >
                                    {ingestionState === 'ingesting' && (
                                        <>
                                            <div className="flex gap-2 mb-4">
                                                {[0, 1, 2].map(i => (
                                                    <motion.div
                                                        key={i}
                                                        initial={{ opacity: 0, y: 10 }}
                                                        animate={{ opacity: 1, y: 0 }}
                                                        transition={{ delay: i * 0.1 }}
                                                    >
                                                        <FileCode className="w-8 h-8 text-muted/50" />
                                                    </motion.div>
                                                ))}
                                            </div>
                                            <h3 className="text-primary font-medium mb-1">Capturing code snapshot...</h3>
                                            <p className="text-xs text-muted font-mono">Indexing 24 files • 1,420 lines</p>
                                        </>
                                    )}

                                    {ingestionState === 'confirmed' && (
                                        <div className="flex flex-col items-center">
                                            <motion.div
                                                initial={{ scale: 0.8, opacity: 0 }}
                                                animate={{ scale: 1, opacity: 1 }}
                                                className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center mb-3 border border-emerald-500/20"
                                            >
                                                <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                                            </motion.div>
                                            <h3 className="text-emerald-400 font-medium text-sm">Snapshot Captured Successfully</h3>
                                            <p className="text-xs text-muted mt-1 flex items-center gap-1">
                                                <Lock className="w-3 h-3" /> Input locked for immutable analysis
                                            </p>
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </form>
                </div>

                <div className="px-6 py-3 flex items-center gap-4 text-xs text-muted font-mono border-t border-border bg-secondary/50 rounded-b-card">
                    <span>SUPPORTED ENGINES:</span>
                    <div className="flex gap-3">
                        <span className="text-text-secondary">JAVA</span>
                        <span className="text-text-secondary">JS</span>
                        <span className="text-text-secondary">PYTHON</span>
                        <span className="text-text-secondary">TYPESCRIPT</span>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default InputPanel;
