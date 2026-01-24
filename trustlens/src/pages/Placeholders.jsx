import React from 'react';

const PlaceholderPage = ({ title }) => (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center p-8">
        <h1 className="text-3xl font-bold text-slate-200 mb-4">{title}</h1>
        <p className="text-slate-500 max-w-md">This module is part of the enterprise suite. Implementation pending for this hackathon demo.</p>
    </div>
);

export const AgentsPage = () => <PlaceholderPage title="Agent Capabilities" />;
export const ConflictsPage = () => <PlaceholderPage title="Conflict Resolution Center" />;
export const ReportPage = () => <PlaceholderPage title="Audit Report Generation" />;
export const HistoryPage = () => <PlaceholderPage title="Analysis History" />;
export const SettingsPage = () => <PlaceholderPage title="System Settings" />;
