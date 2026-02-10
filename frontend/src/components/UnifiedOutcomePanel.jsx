import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, ShieldAlert, AlertTriangle, Lock, ArrowRight, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

const UnifiedOutcomePanel = ({ decision, overall, report }) => {
    if (!decision || !overall) return null;

    // Configuration based on decision
    const CONFIG = {
        SAFE: {
            theme: "emerald",
            gradient: "from-emerald-400 to-teal-500",
            glow: "bg-emerald-500/20",
            border: "border-emerald-500/30",
            icon: ShieldCheck,
            title: "SAFE TO PROCEED",
            textColor: "text-emerald-400",
            description: "No critical vulnerabilities detected. System consensus is strong."
        },
        CAUTION: {
            theme: "yellow",
            gradient: "from-yellow-400 to-orange-500",
            glow: "bg-yellow-500/20",
            border: "border-yellow-500/30",
            icon: AlertTriangle,
            title: "PROCEED WITH CAUTION",
            textColor: "text-yellow-400",
            description: "Minor issues detected. Review recommendations before deployment."
        },
        MANUAL_REVIEW: {
            theme: "orange",
            gradient: "from-orange-400 to-red-500",
            glow: "bg-orange-500/20",
            border: "border-orange-500/30",
            icon: Lock,
            title: "MANUAL REVIEW REQUIRED",
            textColor: "text-orange-400",
            description: "Agents detected conflicting signals. Human oversight is mandatory."
        },
        RISK: {
            theme: "red",
            gradient: "from-red-500 to-rose-600",
            glow: "bg-red-500/20", // Stronger glow
            border: "border-red-500/50",
            icon: ShieldAlert,
            title: "CRITICAL RISK DETECTED",
            textColor: "text-red-500",
            description: "Critical security flaws found. Deployment blocked."
        }
    };

    const activeConfig = CONFIG[decision] || CONFIG.SAFE;
    const Icon = activeConfig.icon;
    const confidencePercent = Math.round(overall.confidence * 100);

    return (
        <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.99 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.4 }}
            className={`w-full max-w-6xl mx-auto mb-8 rounded-2xl border ${activeConfig.border} bg-surface/40 backdrop-blur-xl relative overflow-hidden shadow-lg`}
        >
            {/* Global Noise Texture Overlay */}
            <div className="absolute inset-0 opacity-[0.03] bg-noise pointer-events-none mix-blend-overlay" />

            {/* Ambient Animated Glow - Reduced size */}
            <div className={`absolute top-0 right-0 w-[400px] h-[400px] ${activeConfig.glow} blur-[100px] rounded-full opacity-20 pointer-events-none`} />

            <div className="relative z-10 p-6 flex flex-col md:flex-row items-center justify-between gap-8">

                {/* Left Side: Verdict & Description */}
                <div className="flex-1 flex items-start gap-5 text-left">
                    {/* Icon */}
                    <div className={`shrink-0 p-3 rounded-xl bg-surface border border-white/5 shadow-inner`}>
                        <Icon className={`w-8 h-8 ${activeConfig.textColor}`} />
                    </div>

                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <span className={`text-[10px] font-mono uppercase tracking-widest ${activeConfig.textColor} opacity-80`}>
                                VERDICT
                            </span>
                            <div className={`h-px w-8 bg-gradient-to-r from-${activeConfig.theme}-500/50 to-transparent`} />
                        </div>

                        <h1 className={`text-2xl md:text-3xl font-bold tracking-tight mb-2 bg-clip-text text-transparent bg-gradient-to-br ${activeConfig.gradient}`}>
                            {activeConfig.title}
                        </h1>

                        <p className="text-sm text-slate-300 max-w-lg leading-relaxed font-light">
                            {activeConfig.description}
                        </p>
                    </div>
                </div>

                {/* Right Side: Metrics & Action */}
                <div className="flex items-center gap-6 shrink-0 bg-white/5 rounded-xl p-4 border border-white/5">

                    {/* Confidence Metric - Compact */}
                    <div className="flex flex-col items-end border-r border-white/10 pr-6 mr-2">
                        <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-0.5">Confidence</div>
                        <div className="flex items-baseline gap-1">
                            <span className="text-2xl font-mono font-bold text-white">{confidencePercent}%</span>
                            <span className={`text-xs ${activeConfig.textColor}`}>
                                {activeConfig.theme === 'emerald' ? 'High' : activeConfig.theme === 'red' ? 'Critical' : 'Moderate'}
                            </span>
                        </div>
                    </div>

                    {/* Action Button - Compact */}
                    <Link
                        to="/report"
                        className={`group relative flex items-center gap-2 px-5 py-2.5 rounded-lg font-semibold text-sm text-white bg-gradient-to-br ${activeConfig.gradient} hover:shadow-lg transition-all overflow-hidden`}
                    >
                        <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                        <span className="relative z-10">Full Report</span>
                        <ArrowRight className="w-4 h-4 relative z-10 group-hover:translate-x-1 transition-transform" />
                    </Link>
                </div>

            </div>
        </motion.div>
    );
};

export default UnifiedOutcomePanel;
