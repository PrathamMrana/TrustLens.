import React from 'react';
import { ShieldCheck } from 'lucide-react';
import { APP_CONFIG } from '../utils/constants';

const Header = () => {
    return (
        <header className="w-full py-6 px-8 border-b border-white/10 bg-background/50 backdrop-blur-md sticky top-0 z-50">
            <div className="max-w-5xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                        <ShieldCheck className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-xl font-semibold tracking-tight text-white/90">
                            {APP_CONFIG.name}
                        </h1>
                        <p className="text-xs text-white/40 uppercase tracking-widest font-medium">
                            {APP_CONFIG.subtitle}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span className="text-xs text-emerald-500/80 font-mono">SYSTEM ONLINE</span>
                </div>
            </div>
        </header>
    );
};

export default Header;
