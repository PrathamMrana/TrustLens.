import React from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, AlertTriangle, CheckCircle, Shield } from 'lucide-react';

const KeyInsights = ({ results }) => {
    if (!results || results.length === 0) return null;

    // Extract factual insights directly from backend data
    const highRiskAgents = results.filter(r => r.risk === 'high');
    const safeAgents = results.filter(r => r.risk === 'low');
    const disagreements = results.length > 0 && highRiskAgents.length > 0 && safeAgents.length > 0;

    const insights = [];

    if (disagreements) {
        insights.push({
            type: 'warning',
            text: "The system detected conflicting assessments between experts.",
            icon: AlertTriangle
        });
    }

    if (highRiskAgents.length > 0) {
        const names = highRiskAgents.map(a => a.name).join(' and ');
        insights.push({
            type: 'critical',
            text: `${names} reported critical findings requiring review.`,
            icon: Shield
        });
    } else if (safeAgents.length === results.length) {
        insights.push({
            type: 'success',
            text: "All active agents reported logic and security within safe parameters.",
            icon: CheckCircle
        });
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {insights.map((insight, idx) => (
                <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.2 }}
                    className={`p-4 rounded-card border flex items-start gap-3 backdrop-blur-sm
             ${insight.type === 'critical' ? 'bg-security/5 border-security/20' :
                            insight.type === 'warning' ? 'bg-uncertainty/5 border-uncertainty/20' :
                                'bg-logic/5 border-logic/20'}
           `}
                >
                    <div className={`p-2 rounded-lg 
             ${insight.type === 'critical' ? 'bg-security/10 text-security' :
                            insight.type === 'warning' ? 'bg-uncertainty/10 text-uncertainty' :
                                'bg-logic/10 text-logic'}
           `}>
                        <insight.icon className="w-5 h-5" />
                    </div>
                    <div>
                        <h4 className={`text-sm font-semibold mb-1
               ${insight.type === 'critical' ? 'text-security' :
                                insight.type === 'warning' ? 'text-uncertainty' :
                                    'text-logic'}
             `}>
                            Key Observation
                        </h4>
                        <p className="text-sm text-text-secondary leading-relaxed">
                            {insight.text}
                        </p>
                    </div>
                </motion.div>
            ))}
        </div>
    );
};

export default KeyInsights;
