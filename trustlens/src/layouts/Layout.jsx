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
            "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300",
            active
                ? "bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.2)]"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
        )}
    >
        <Icon className="w-4 h-4" />
        <span className="text-xs font-semibold uppercase tracking-wider">{label}</span>
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
                        transition={{ duration: 0.5, ease: "easeOut" }}
                        className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
                    >
                        <nav className="flex items-center gap-1 p-2 bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-full shadow-2xl ring-1 ring-white/5">
                            <NavItem to="/" icon={ShieldCheck} label="Home" active={location.pathname === '/'} />
                            <div className="w-px h-4 bg-white/10 mx-1" />
                            <NavItem to="/agents" icon={Info} label="Agents" active={location.pathname === '/agents'} />
                            <NavItem to="/conflicts" icon={AlertTriangle} label="Conflicts" active={location.pathname === '/conflicts'} />
                            <div className="w-px h-4 bg-white/10 mx-1" />
                            <NavItem to="/settings" icon={Settings} label="Settings" active={location.pathname === '/settings'} />
                        </nav>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Layout;
