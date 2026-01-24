import React from 'react';
import { NavLink } from 'react-router-dom';
import { ShieldCheck, Info, AlertTriangle, Settings } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const NavItem = ({ to, icon: Icon, label }) => (
    <NavLink
        to={to}
        className={({ isActive }) => clsx(
            "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300",
            isActive
                ? "bg-blue-500/20 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.3)] border border-blue-500/30"
                : "text-slate-400 hover:text-white hover:bg-white/5"
        )}
    >
        <Icon className="w-4 h-4" />
        <span className="text-xs font-semibold uppercase tracking-wider">{label}</span>
    </NavLink>
);

const FloatingNav = ({ isVisible }) => {
    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    className="fixed top-6 left-1/2 -translate-x-1/2 z-50"
                >
                    <nav className="flex items-center gap-2 p-2 bg-slate-900/60 backdrop-blur-md border border-white/10 rounded-full shadow-2xl">
                        <NavItem to="/" icon={ShieldCheck} label="Home" />
                        <div className="w-px h-4 bg-white/10 mx-1" />
                        <NavItem to="/agents" icon={Info} label="Agents" />
                        <NavItem to="/conflicts" icon={AlertTriangle} label="Conflicts" />
                        {/* History removed per requirement */}
                        <div className="w-px h-4 bg-white/10 mx-1" />
                        <NavItem to="/settings" icon={Settings} label="Settings" />
                    </nav>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default FloatingNav;
