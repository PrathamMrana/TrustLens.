import React from 'react';
import { motion } from 'framer-motion';
import { FileCode, Code2, Languages } from 'lucide-react';

const RepoMetadataCard = ({ metadata, status }) => {
    if (!metadata) return null;

    // Determine if we're in loading state
    const isLoading = status === 'ANALYZING' || status === 'UPLOADING';
    const isFailed = status === 'FAILED';

    // Determine display values
    const getDisplayValue = (value) => {
        if (isLoading) return null; // Will show skeleton
        if (isFailed || value === undefined || value === null || value === 0) return '—';
        return typeof value === 'number' ? value.toLocaleString() : value;
    };

    const displayName = isLoading
        ? 'Analyzing Repository'
        : isFailed
            ? 'Repository Metadata Unavailable'
            : (metadata.repoName && metadata.repoName !== 'Unknown Repository')
                ? metadata.repoName
                : '—';

    const displaySubtitle = isLoading ? 'Extracting structure and metadata' : 'Repository Analysis';

    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-xl border border-white/10 bg-gradient-to-br from-slate-900/50 to-slate-800/30 backdrop-blur-sm"
        >
            <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <Code2 className="w-4 h-4 text-blue-400" />
                </div>
                <div>
                    <h3 className="text-sm font-semibold text-slate-200">{displayName}</h3>
                    <p className="text-xs text-slate-500">{displaySubtitle}</p>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
                {/* Files */}
                <div className="flex items-center gap-2">
                    <FileCode className="w-4 h-4 text-slate-400" />
                    <div>
                        {isLoading ? (
                            <div className="h-6 w-12 bg-slate-700/50 rounded animate-pulse"></div>
                        ) : (
                            <div className="text-lg font-bold text-white">{getDisplayValue(metadata.files)}</div>
                        )}
                        <div className="text-[10px] text-slate-500 uppercase tracking-wide">Files</div>
                    </div>
                </div>

                {/* Lines */}
                <div className="flex items-center gap-2">
                    <Code2 className="w-4 h-4 text-slate-400" />
                    <div>
                        {isLoading ? (
                            <div className="h-6 w-16 bg-slate-700/50 rounded animate-pulse"></div>
                        ) : (
                            <div className="text-lg font-bold text-white">{getDisplayValue(metadata.lines)}</div>
                        )}
                        <div className="text-[10px] text-slate-500 uppercase tracking-wide">Lines</div>
                    </div>
                </div>

                {/* Languages */}
                <div className="flex items-center gap-2">
                    <Languages className="w-4 h-4 text-slate-400" />
                    <div>
                        {isLoading ? (
                            <div className="h-6 w-8 bg-slate-700/50 rounded animate-pulse"></div>
                        ) : (
                            <div className="text-lg font-bold text-white">
                                {metadata.languages && metadata.languages.length > 0 ? metadata.languages.length : '—'}
                            </div>
                        )}
                        <div className="text-[10px] text-slate-500 uppercase tracking-wide">Languages</div>
                    </div>
                </div>
            </div>

            {/* Language Tags */}
            {!isLoading && !isFailed && metadata.languages && metadata.languages.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/5">
                    <div className="flex flex-wrap gap-2">
                        {metadata.languages.slice(0, 5).map((lang, index) => (
                            <span
                                key={index}
                                className="px-2 py-1 text-[10px] font-medium rounded-md bg-blue-500/10 text-blue-300 border border-blue-500/20"
                            >
                                {lang}
                            </span>
                        ))}
                        {metadata.languages.length > 5 && (
                            <span className="px-2 py-1 text-[10px] font-medium rounded-md bg-slate-700/50 text-slate-400">
                                +{metadata.languages.length - 5} more
                            </span>
                        )}
                    </div>
                </div>
            )}

            {/* Loading skeleton for language tags */}
            {isLoading && (
                <div className="mt-3 pt-3 border-t border-white/5">
                    <div className="flex flex-wrap gap-2">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-6 w-16 bg-slate-700/50 rounded animate-pulse"></div>
                        ))}
                    </div>
                </div>
            )}
        </motion.div>
    );
};

export default RepoMetadataCard;
