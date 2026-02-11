import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Shield, Zap, Activity, Users, Lock, ChevronRight, Play, AlertTriangle, CheckCircle2, FileSearch, Scale } from 'lucide-react';
import { Link } from 'react-router-dom';
import HowItWorksModal from '../components/HowItWorksModal';

// --- Components ---

const HeroSection = ({ onOpenModal }) => (
    <div className="relative min-h-[90vh] flex flex-col items-center justify-center text-center px-4 overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 z-0 bg-background">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/10 rounded-full blur-[120px] animate-pulse" />
            <div className="absolute top-1/3 left-1/4 w-[400px] h-[400px] bg-accent-cyan/10 rounded-full blur-[100px]" />
            {/* Grain Overlay */}
            <div className="absolute inset-0 bg-noise opacity-30 pointer-events-none mix-blend-overlay" />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-6xl mx-auto space-y-10">
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
            >
                <div className="relative inline-block mb-6 group cursor-default">
                    <span className="absolute -inset-1 rounded-full bg-gradient-to-r from-blue-600 to-accent-cyan opacity-20 blur-xl animate-pulse group-hover:opacity-40 transition-opacity duration-500"></span>
                    <span className="relative inline-block py-1.5 px-5 rounded-full bg-surface/80 border border-white/10 text-xs font-mono text-accent-cyan tracking-[0.25em] backdrop-blur-md shadow-lg">
                        MULTI-AGENT INTELLIGENCE v2.0
                    </span>
                </div>

                <h1 className="text-7xl md:text-[9rem] font-black tracking-tighter text-white mb-8 leading-[0.9] drop-shadow-2xl select-none">
                    <span className="block text-transparent bg-clip-text bg-gradient-to-b from-white via-white to-white/40">Trust</span>
                    <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-accent-cyan to-blue-400 animate-gradient-x">Lens</span>
                </h1>

                <p className="text-2xl md:text-4xl text-text-secondary max-w-4xl mx-auto leading-relaxed font-light tracking-wide">
                    The intelligence that <span className="text-white font-medium border-b border-blue-500/50">explains</span>, rather than <span className="text-white font-medium border-b border-red-500/50">guesses</span>.
                </p>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-8"
            >
                <Link to="/analyze" className="group relative px-10 py-5 bg-blue-600 rounded-full overflow-hidden transition-all hover:bg-blue-500 shadow-xl shadow-blue-500/20 hover:shadow-blue-500/40 hover:scale-105 active:scale-95">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 ease-in-out" />
                    <span className="relative flex items-center gap-3 font-bold text-lg text-white tracking-wide">
                        Analyze Code <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                    </span>
                </Link>
                <button
                    onClick={onOpenModal}
                    className="group px-10 py-5 rounded-full border border-white/10 hover:bg-white/5 text-text-secondary hover:text-white transition-all hover:scale-105 active:scale-95 font-medium tracking-wide flex items-center gap-3"
                >
                    <Play className="w-4 h-4 fill-current opacity-50 group-hover:opacity-100 transition-opacity" />
                    How It Works
                </button>
            </motion.div>
        </div>
    </div>
);

const IntelligenceOverview = () => {
    const agents = [
        { name: "Security", color: "text-security", border: "border-security/30", bg: "bg-security/5", icon: Lock },
        { name: "Logic", color: "text-logic", border: "border-logic/30", bg: "bg-logic/5", icon: Zap },
        { name: "Quality", color: "text-quality", border: "border-quality/30", bg: "bg-quality/5", icon: Activity },
    ];

    return (
        <section id="how-it-works" className="py-24 bg-background relative border-t border-border">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">How TrustLens Thinks</h2>
                    <p className="text-text-secondary max-w-2xl mx-auto">
                        We don't rely on a single opaque model. Your code is debated by specialized agents.
                    </p>
                </div>

                <div className="relative flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16">
                    {/* Connecting Lines (Desktop) */}
                    <div className="hidden md:block absolute top-1/2 left-20 right-20 h-px bg-gradient-to-r from-transparent via-border to-transparent -z-10" />

                    {agents.map((agent, i) => (
                        <motion.div
                            key={agent.name}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.2 }}
                            className={`relative p-8 rounded-card border ${agent.border} ${agent.bg} backdrop-blur-sm w-full md:w-64 text-center group hover:-translate-y-2 transition-transform duration-500`}
                        >
                            <div className={`mx-auto w-12 h-12 rounded-full flex items-center justify-center mb-4 ${agent.bg} border ${agent.border}`}>
                                <agent.icon className={`w-6 h-6 ${agent.color}`} />
                            </div>
                            <h3 className={`text-lg font-bold mb-2 ${agent.color}`}>{agent.name}</h3>
                            <p className="text-sm text-muted">Analyzes specialized patterns and flags risks independently.</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

const ComparisonSection = () => (
    <section className="py-24 bg-secondary">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
                <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Why Single-Model AI Fails in High-Risk Systems</h2>
                <div className="space-y-6">
                    <div className="flex gap-4 p-4 rounded-xl bg-background/50 border border-border">
                        <div className="mt-1"><Users className="w-5 h-5 text-muted" /></div>
                        <div>
                            <h4 className="text-white font-semibold mb-1">Traditional AI</h4>
                            <p className="text-sm text-muted">Forces an answer even when uncertain. Opaque reasoning. No checks and balances.</p>
                        </div>
                    </div>
                    <div className="flex gap-4 p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
                        <div className="mt-1"><Shield className="w-5 h-5 text-blue-400" /></div>
                        <div>
                            <h4 className="text-white font-semibold mb-1">TrustLens Architecture</h4>
                            <p className="text-sm text-text-secondary">Orchestrates multiple experts. Surfaces conflict. Does not guess.</p>
                        </div>
                    </div>
                </div>
            </div>
            <div className="relative h-[400px] bg-background rounded-2xl border border-border overflow-hidden flex items-center justify-center">
                {/* Visual Abstraction of "Orchestrator" */}
                <div className="absolute inset-0 bg-grid-white/[0.02]" />
                <div className="relative z-10 text-center">
                    <div className="w-32 h-32 rounded-full border-2 border-dashed border-blue-500/30 flex items-center justify-center mx-auto mb-4 animate-[spin_10s_linear_infinite]">
                        <div className="w-24 h-24 rounded-full bg-blue-500/10 flex items-center justify-center">
                            <Shield className="w-10 h-10 text-blue-400" />
                        </div>
                    </div>
                    <div className="text-sm font-mono text-blue-400">ORCHESTRATOR ONLINE</div>
                    <div className="text-xs text-muted mt-2">Evaluating 4 streams...</div>
                </div>
            </div>
        </div>
    </section>
);

const ConfidenceSection = () => (
    <section className="py-24 bg-background overflow-hidden relative">
        <div className="max-w-4xl mx-auto text-center px-6 relative z-10">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Confidence Is a Feature</h2>
            <p className="text-text-secondary mb-12 max-w-xl mx-auto">
                TrustLens doesn't just output code. It outputs a confidence score for every decision.
                If uncertainty is high, it recommends manual review.
            </p>

            <div className="relative w-64 h-32 mx-auto overflow-hidden">
                <div className="absolute bottom-0 w-64 h-64 rounded-full border-[20px] border-surface border-t-emerald-500 border-r-emerald-500/30 transform transition-all duration-1000 rotate-[-45deg] hover:rotate-0"></div>
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center pb-2">
                    <div className="text-4xl font-bold text-white">98.2%</div>
                    <div className="text-xs text-emerald-500 uppercase tracking-widest font-bold">Confidence</div>
                </div>
            </div>
            <div className="mt-8 flex justify-center gap-8 text-sm">
                <div className="flex items-center gap-2 text-emerald-400"><CheckCircle2 className="w-4 h-4" /> High Confidence</div>
                <div className="flex items-center gap-2 text-yellow-500"><AlertTriangle className="w-4 h-4" /> Conflict Detected</div>
                <div className="flex items-center gap-2 text-purple-400"><Users className="w-4 h-4" /> Manual Review</div>
            </div>
        </div>
    </section>
);

const UseCaseSection = () => {
    const cases = [
        { title: "Code Intelligence", desc: "Automated review for security & logic bugs.", icon: FileSearch },
        { title: "Risk Compliance", desc: "Evaluate against strict enterprise policies.", icon: Shield },
        { title: "System Auditing", desc: "Deep architectural analysis of legacy code.", icon: Scale },
    ];

    return (
        <section className="py-24 bg-secondary">
            <div className="max-w-6xl mx-auto px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Built for Decisions That Matter</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {cases.map((c, i) => (
                        <motion.div
                            key={c.title}
                            whileHover={{ y: -5 }}
                            className="p-8 rounded-card bg-background border border-border group hover:border-blue-500/50 transition-colors"
                        >
                            <div className="w-12 h-12 bg-surface rounded-lg flex items-center justify-center mb-6 group-hover:bg-blue-500/10 transition-colors">
                                <c.icon className="w-6 h-6 text-text-secondary group-hover:text-blue-400 transition-colors" />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">{c.title}</h3>
                            <p className="text-text-secondary text-sm">{c.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

const TrustBadgeSection = () => (
    <div className="py-12 bg-background border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap justify-center gap-8 md:gap-16 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
            {["Designed for Explainability", "Collaboration over Automation", "Human-in-the-Loop Core"].map((text) => (
                <div key={text} className="flex items-center gap-2 text-sm font-medium text-white uppercase tracking-wider">
                    <Shield className="w-4 h-4" /> {text}
                </div>
            ))}
        </div>
    </div>
);

const LandingPage = () => {
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
        <div className="min-h-screen bg-background text-text-primary selection:bg-blue-500/30">
            <HeroSection onOpenModal={() => setIsModalOpen(true)} />
            <IntelligenceOverview />
            <ComparisonSection />
            <ConfidenceSection />
            <UseCaseSection />
            <TrustBadgeSection />

            <section className="py-32 bg-background text-center px-4 relative overflow-hidden">
                <div className="absolute inset-0 bg-blue-600/5 radial-gradient" />
                <div className="relative z-10 max-w-3xl mx-auto">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-8">Don't Ask AI to Guess.<br />Ask It to Reason.</h2>
                    <Link to="/analyze" className="inline-flex items-center gap-2 px-8 py-4 bg-white text-background rounded-lg font-bold hover:bg-gray-100 transition-colors shadow-2xl">
                        Start an Analysis <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>
            </section>

            {/* How It Works Modal */}
            <HowItWorksModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </div>
    );
};

export default LandingPage;
