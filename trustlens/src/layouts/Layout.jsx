import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import Header from '../components/Header';
import { ShieldCheck, Info, AlertTriangle, Settings } from 'lucide-react';
import clsx from 'clsx';
import { AnimatePresence, motion } from 'framer-motion';

const NavItem = ({ to, icon: Icon, label, active }) => (
    <Link
        to={to}
        className={clsx(
            "flex items-center gap-2 px-4 py-2.5 rounded-full transition-all duration-300 ease-out relative",
            active
                ? "bg-gradient-to-br from-blue-500/20 to-blue-600/10 text-blue-200 shadow-[0_0_20px_rgba(59,130,246,0.25),0_0_40px_rgba(59,130,246,0.1)] ring-1 ring-blue-400/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.08] hover:shadow-[0_0_15px_rgba(255,255,255,0.05)]"
        )}
    >
        <Icon className="w-4 h-4" strokeWidth={1.8} />
        <span className="text-[11px] font-medium uppercase tracking-wide">{label}</span>
    </Link>
);

const Layout = () => {
    const location = useLocation();
    const isLandingPage = location.pathname === '/';

    return (
        <div className="min-h-screen bg-background text-slate-200 font-sans selection:bg-blue-500/30 flex flex-col">
            {/* Header - Hidden on Landing Page */}
            {!isLandingPage && <Header />}

            {/* Main content */}
            <main className="flex-grow relative">
                <Outlet />
            </main>

            {/* Floating Bottom Navigation - Hidden on Landing Page */}
            <AnimatePresence>
                {!isLandingPage && (
                    <motion.div
                        initial={{ y: 100, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 100, opacity: 0 }}
                        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                        className="fixed bottom-8 left-1/2 -translate-x-1/2 z-40 pb-safe"
                    >
                        <nav className="group relative flex items-center gap-1.5 px-5 py-3 
                            bg-gradient-to-b from-slate-800/70 to-slate-900/80 
                            backdrop-blur-2xl 
                            border border-white/[0.08] 
                            rounded-full 
                            shadow-[0_8px_32px_rgba(0,0,0,0.6),0_20px_60px_rgba(0,0,0,0.4),0_0_0_1px_rgba(255,255,255,0.05)_inset] 
                            opacity-85 
                            hover:opacity-100 
                            hover:bg-gradient-to-b hover:from-slate-800/80 hover:to-slate-900/90
                            hover:border-white/[0.12] 
                            hover:shadow-[0_8px_32px_rgba(0,0,0,0.7),0_20px_60px_rgba(0,0,0,0.5),0_0_40px_rgba(59,130,246,0.15),0_0_0_1px_rgba(255,255,255,0.08)_inset]
                            transition-all duration-500 ease-out
                            before:absolute before:inset-0 before:rounded-full before:bg-gradient-to-b before:from-white/[0.08] before:to-transparent before:pointer-events-none">
                            <NavItem to="/" icon={ShieldCheck} label="Home" active={location.pathname === '/'} />
                            <div className="w-px h-4 bg-gradient-to-b from-transparent via-white/10 to-transparent mx-1" />
                            <NavItem to="/agents" icon={Info} label="Agents" active={location.pathname === '/agents'} />
                            <NavItem to="/conflicts" icon={AlertTriangle} label="Conflicts" active={location.pathname === '/conflicts'} />
                            <div className="w-px h-4 bg-gradient-to-b from-transparent via-white/10 to-transparent mx-1" />
                            <NavItem to="/settings" icon={Settings} label="Settings" active={location.pathname === '/settings'} />
                        </nav>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Layout;
