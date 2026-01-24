import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronRight, ChevronLeft, GitBranch, FolderGit2, Cloud, Code2, Network, Shield, Brain, BarChart3, Puzzle, AlertTriangle, TrendingUp, CheckCircle2, Eye, Zap, Target } from 'lucide-react';
import { Link } from 'react-router-dom';

const HowItWorksModal = ({ isOpen, onClose }) => {
    const [currentStep, setCurrentStep] = useState(0);

    // ESC key handler
    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [isOpen, onClose]);

    // Reset to first step when modal opens
    useEffect(() => {
        if (isOpen) {
            setCurrentStep(0);
        }
    }, [isOpen]);

    const steps = [
        {
            title: "Ingestion",
            subtitle: "Secure Repository Import",
            description: "Your repository is securely ingested from GitHub or ZIP and structured for analysis.",
            icon: <Cloud className="w-16 h-16" />,
            animation: "cloud"
        },
        {
            title: "Structural Understanding",
            subtitle: "Deep Code Analysis",
            description: "TrustLens extracts structural and semantic features from your codebase.",
            icon: <Network className="w-16 h-16" />,
            animation: "graph"
        },
        {
            title: "Multi-Agent Intelligence",
            subtitle: "Expert Perspectives",
            description: "Independent expert agents analyze the same code from different perspectives.",
            icon: <Brain className="w-16 h-16" />,
            animation: "agents"
        },
        {
            title: "Conflict Detection",
            subtitle: "Uncertainty Recognition",
            description: "When agents disagree, TrustLens detects uncertainty instead of forcing conclusions.",
            icon: <AlertTriangle className="w-16 h-16" />,
            animation: "conflict"
        },
        {
            title: "Final Decision",
            subtitle: "Transparent Results",
            description: "Confidence, risk, and disagreement are combined into a transparent decision.",
            icon: <Target className="w-16 h-16" />,
            animation: "decision"
        }
    ];

    const agents = [
        { name: "Security Agent", icon: Shield, color: "from-red-500 to-orange-500", delay: 0 },
        { name: "Logic Agent", icon: Brain, color: "from-blue-500 to-cyan-500", delay: 0.2 },
        { name: "Code Quality", icon: BarChart3, color: "from-green-500 to-emerald-500", delay: 0.4 },
        { name: "Feature Agent", icon: Puzzle, color: "from-purple-500 to-pink-500", delay: 0.6 }
    ];

    const differentiators = [
        {
            icon: Eye,
            title: "Explainable Decisions",
            description: "Every result is traceable to agent reasoning"
        },
        {
            icon: Zap,
            title: "No Guessing",
            description: "Low confidence triggers human review"
        },
        {
            icon: CheckCircle2,
            title: "Built for Trust",
            description: "Designed to assist, not replace, engineers"
        }
    ];

    const handleNext = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handlePrevious = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const renderStepAnimation = () => {
        const step = steps[currentStep];

        switch (step.animation) {
            case "cloud":
                return (
                    <div className="flex items-center justify-center gap-8">
                        <motion.div
                            initial={{ opacity: 0, x: -50 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.6 }}
                        >
                            <GitBranch className="w-20 h-20 text-accent-cyan" />
                        </motion.div>
                        <motion.div
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.6, delay: 0.3 }}
                        >
                            <ChevronRight className="w-12 h-12 text-text-secondary" />
                        </motion.div>
                        <motion.div
                            initial={{ opacity: 0, x: 50 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.6, delay: 0.6 }}
                        >
                            <Cloud className="w-20 h-20 text-blue-500" />
                        </motion.div>
                    </div>
                );

            case "graph":
                return (
                    <div className="relative w-full h-48 flex items-center justify-center">
                        <motion.div
                            className="absolute"
                            initial={{ opacity: 1 }}
                            animate={{ opacity: 0 }}
                            transition={{ duration: 0.8, delay: 0.5 }}
                        >
                            <Code2 className="w-24 h-24 text-accent-cyan" />
                        </motion.div>
                        <motion.div
                            className="grid grid-cols-3 gap-4"
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.8, delay: 1 }}
                        >
                            {[...Array(6)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500"
                                    initial={{ opacity: 0, scale: 0 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ duration: 0.3, delay: 1 + i * 0.1 }}
                                />
                            ))}
                        </motion.div>
                    </div>
                );

            case "agents":
                return (
                    <div className="grid grid-cols-2 gap-6 max-w-2xl mx-auto">
                        {agents.map((agent, idx) => (
                            <motion.div
                                key={agent.name}
                                className="relative p-6 rounded-2xl bg-surface/30 backdrop-blur-md border border-white/10 overflow-hidden group"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: agent.delay }}
                            >
                                <motion.div
                                    className={`absolute inset-0 bg-gradient-to-br ${agent.color} opacity-0 group-hover:opacity-10 transition-opacity`}
                                    animate={{ opacity: [0.1, 0.2, 0.1] }}
                                    transition={{ duration: 2, repeat: Infinity, delay: agent.delay }}
                                />
                                <div className="relative flex items-center gap-4">
                                    <div className={`p-3 rounded-xl bg-gradient-to-br ${agent.color}`}>
                                        <agent.icon className="w-6 h-6 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="font-semibold text-white">{agent.name}</h4>
                                        <motion.div
                                            className="mt-2 h-1 bg-white/20 rounded-full overflow-hidden"
                                            initial={{ width: 0 }}
                                            animate={{ width: "100%" }}
                                            transition={{ duration: 1, delay: agent.delay + 0.5 }}
                                        >
                                            <motion.div
                                                className={`h-full bg-gradient-to-r ${agent.color}`}
                                                initial={{ width: "0%" }}
                                                animate={{ width: "100%" }}
                                                transition={{ duration: 1.5, delay: agent.delay + 0.5 }}
                                            />
                                        </motion.div>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                );

            case "conflict":
                return (
                    <div className="flex items-center justify-center gap-8">
                        <motion.div
                            className="p-6 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500"
                            initial={{ x: 0, rotate: 0 }}
                            animate={{ x: -30, rotate: -10 }}
                            transition={{ duration: 0.8, delay: 0.3 }}
                        >
                            <Shield className="w-16 h-16 text-white" />
                        </motion.div>
                        <motion.div
                            className="relative"
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.5, delay: 1.1 }}
                        >
                            <div className="absolute inset-0 bg-red-500/20 blur-xl animate-pulse" />
                            <AlertTriangle className="relative w-20 h-20 text-red-500" />
                        </motion.div>
                        <motion.div
                            className="p-6 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500"
                            initial={{ x: 0, rotate: 0 }}
                            animate={{ x: 30, rotate: 10 }}
                            transition={{ duration: 0.8, delay: 0.3 }}
                        >
                            <Brain className="w-16 h-16 text-white" />
                        </motion.div>
                    </div>
                );

            case "decision":
                return (
                    <div className="space-y-8 max-w-md mx-auto">
                        <div className="space-y-3">
                            <div className="flex justify-between text-sm">
                                <span className="text-text-secondary">Confidence Level</span>
                                <motion.span
                                    className="text-accent-cyan font-semibold"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.5 }}
                                >
                                    87%
                                </motion.span>
                            </div>
                            <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-blue-500 to-accent-cyan"
                                    initial={{ width: "0%" }}
                                    animate={{ width: "87%" }}
                                    transition={{ duration: 1.5, delay: 0.3 }}
                                />
                            </div>
                        </div>
                        <motion.div
                            className="p-6 rounded-2xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 1.5 }}
                        >
                            <div className="flex items-center gap-3">
                                <CheckCircle2 className="w-8 h-8 text-green-500" />
                                <div>
                                    <div className="font-semibold text-white">SAFE</div>
                                    <div className="text-sm text-text-secondary">High confidence, low risk</div>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    className="fixed inset-0 z-50 flex items-center justify-center p-4"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                >
                    {/* Backdrop */}
                    <motion.div
                        className="absolute inset-0 bg-black/80 backdrop-blur-md"
                        onClick={onClose}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    />

                    {/* Modal Content */}
                    <motion.div
                        className="relative w-full max-w-4xl max-h-[90vh] bg-background/95 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl overflow-hidden"
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.9, y: 20 }}
                        transition={{ duration: 0.3, type: "spring" }}
                    >
                        {/* Animated Background */}
                        <div className="absolute inset-0 overflow-hidden pointer-events-none">
                            <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-[120px] animate-pulse" />
                            <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent-cyan/10 rounded-full blur-[120px]" />
                        </div>

                        {/* Close Button */}
                        <button
                            onClick={onClose}
                            className="absolute top-6 right-6 z-10 p-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors group"
                        >
                            <X className="w-6 h-6 text-text-secondary group-hover:text-white transition-colors" />
                        </button>

                        {/* Content */}
                        <div className="relative p-12 overflow-y-auto max-h-[90vh]">
                            {/* Header */}
                            <div className="text-center mb-12">
                                <motion.div
                                    className="inline-block mb-4"
                                    key={currentStep}
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ duration: 0.5, type: "spring" }}
                                >
                                    <div className="p-4 rounded-2xl bg-gradient-to-br from-blue-500/20 to-accent-cyan/20 border border-white/10">
                                        {steps[currentStep].icon}
                                    </div>
                                </motion.div>
                                <motion.h2
                                    className="text-4xl font-bold text-white mb-2"
                                    key={`title-${currentStep}`}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.4 }}
                                >
                                    {steps[currentStep].title}
                                </motion.h2>
                                <motion.p
                                    className="text-accent-cyan font-medium"
                                    key={`subtitle-${currentStep}`}
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ duration: 0.4, delay: 0.1 }}
                                >
                                    {steps[currentStep].subtitle}
                                </motion.p>
                            </div>

                            {/* Animation Area */}
                            <motion.div
                                className="mb-12 min-h-[250px] flex items-center justify-center"
                                key={`animation-${currentStep}`}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ duration: 0.5 }}
                            >
                                {renderStepAnimation()}
                            </motion.div>

                            {/* Description */}
                            <motion.p
                                className="text-center text-lg text-text-secondary max-w-2xl mx-auto mb-12"
                                key={`desc-${currentStep}`}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: 0.2 }}
                            >
                                {steps[currentStep].description}
                            </motion.p>

                            {/* Differentiators (only on last step) */}
                            {currentStep === steps.length - 1 && (
                                <motion.div
                                    className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.6, delay: 0.5 }}
                                >
                                    {differentiators.map((item, idx) => (
                                        <motion.div
                                            key={item.title}
                                            className="p-6 rounded-2xl bg-surface/30 backdrop-blur-md border border-white/10 hover:border-accent-cyan/30 transition-all group"
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ duration: 0.5, delay: 0.7 + idx * 0.1 }}
                                            whileHover={{ y: -5 }}
                                        >
                                            <div className="mb-4 p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-accent-cyan/20 inline-block group-hover:scale-110 transition-transform">
                                                <item.icon className="w-6 h-6 text-accent-cyan" />
                                            </div>
                                            <h4 className="font-semibold text-white mb-2">{item.title}</h4>
                                            <p className="text-sm text-text-secondary">{item.description}</p>
                                        </motion.div>
                                    ))}
                                </motion.div>
                            )}

                            {/* Step Indicators */}
                            <div className="flex justify-center gap-2 mb-8">
                                {steps.map((_, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => setCurrentStep(idx)}
                                        className={`h-2 rounded-full transition-all ${idx === currentStep
                                                ? 'w-8 bg-accent-cyan'
                                                : 'w-2 bg-white/20 hover:bg-white/40'
                                            }`}
                                    />
                                ))}
                            </div>

                            {/* Navigation Buttons */}
                            <div className="flex items-center justify-between gap-4">
                                <button
                                    onClick={handlePrevious}
                                    disabled={currentStep === 0}
                                    className="px-6 py-3 rounded-lg border border-border hover:bg-surface text-text-secondary hover:text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-2"
                                >
                                    <ChevronLeft className="w-5 h-5" />
                                    Previous
                                </button>

                                {currentStep === steps.length - 1 ? (
                                    <div className="flex gap-4">
                                        <button
                                            onClick={onClose}
                                            className="px-6 py-3 rounded-lg border border-border hover:bg-surface text-text-secondary hover:text-white transition-colors"
                                        >
                                            Close
                                        </button>
                                        <Link
                                            to="/analyze"
                                            className="px-6 py-3 bg-blue-600 rounded-lg hover:bg-blue-500 text-white font-semibold transition-colors flex items-center gap-2"
                                            onClick={onClose}
                                        >
                                            Analyze My Code
                                            <ChevronRight className="w-5 h-5" />
                                        </Link>
                                    </div>
                                ) : (
                                    <button
                                        onClick={handleNext}
                                        className="px-6 py-3 bg-blue-600 rounded-lg hover:bg-blue-500 text-white font-semibold transition-colors flex items-center gap-2"
                                    >
                                        Next
                                        <ChevronRight className="w-5 h-5" />
                                    </button>
                                )}
                            </div>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default HowItWorksModal;
