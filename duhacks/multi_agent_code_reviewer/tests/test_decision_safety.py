
import unittest
from schemas.agent_output import AgentOutput, AgentType, RiskLevel
from orchestrator.reliability import ReliabilityEngine
from agents.decision_agent import DecisionAgent

class TestDecisionSafety(unittest.TestCase):
    def setUp(self):
        self.reliability_engine = ReliabilityEngine()
        self.decision_agent = DecisionAgent()

    def test_security_only_success(self):
        """1. Only Security agent succeeds -> decision allowed"""
        outputs = [
            AgentOutput(AgentType.SECURITY_ANALYSIS, 0.9, [], RiskLevel.LOW, {}, True),
            AgentOutput(AgentType.LOGIC_ANALYSIS, 0.0, [], RiskLevel.NONE, {}, False)
        ]
        conf = self.reliability_engine.aggregate_confidence(outputs)
        failures = self.reliability_engine.get_failures(outputs)
        
        # Risk assessment
        max_risk = RiskLevel.LOW
        
        should_defer, reason = self.reliability_engine.should_defer(conf, [], failures, max_risk)
        self.assertFalse(should_defer)
        self.assertEqual(conf, 0.9)

    def test_logic_fails_security_succeeds(self):
        """2. Logic agent fails -> system still works (if security succeeds)"""
        outputs = [
            AgentOutput(AgentType.SECURITY_ANALYSIS, 0.85, [], RiskLevel.NONE, {}, True),
            AgentOutput(AgentType.LOGIC_ANALYSIS, 0.0, [], RiskLevel.NONE, {}, False)
        ]
        conf = self.reliability_engine.aggregate_confidence(outputs)
        failures = self.reliability_engine.get_failures(outputs)
        should_defer, reason = self.reliability_engine.should_defer(conf, [], failures, RiskLevel.NONE)
        self.assertFalse(should_defer)

    def test_security_fails_defer(self):
        """3. Security agent fails -> DEFER"""
        outputs = [
            AgentOutput(AgentType.SECURITY_ANALYSIS, 0.0, [], RiskLevel.NONE, {}, False),
            AgentOutput(AgentType.LOGIC_ANALYSIS, 0.9, [], RiskLevel.LOW, {}, True)
        ]
        conf = self.reliability_engine.aggregate_confidence(outputs)
        failures = self.reliability_engine.get_failures(outputs)
        should_defer, reason = self.reliability_engine.should_defer(conf, [], failures, RiskLevel.LOW)
        self.assertTrue(should_defer)
        self.assertIn("Security analysis agent failed", reason)

    def test_conflict_defer(self):
        """4. Conflict exists -> DEFER"""
        outputs = [
            AgentOutput(AgentType.SECURITY_ANALYSIS, 0.9, [], RiskLevel.LOW, {}, True),
            AgentOutput(AgentType.LOGIC_ANALYSIS, 0.9, [], RiskLevel.LOW, {}, True)
        ]
        conflicts = ["Conflict Object"] # Non-empty list
        conf = self.reliability_engine.aggregate_confidence(outputs)
        failures = self.reliability_engine.get_failures(outputs)
        should_defer, reason = self.reliability_engine.should_defer(conf, conflicts, failures, RiskLevel.LOW)
        self.assertTrue(should_defer)
        self.assertIn("unresolved conflicts", reason)

    def test_critical_low_confidence_defer(self):
        """5. CRITICAL risk + confidence < 0.80 -> DEFER"""
        outputs = [
            AgentOutput(AgentType.SECURITY_ANALYSIS, 0.75, [], RiskLevel.CRITICAL, {}, True),
            AgentOutput(AgentType.LOGIC_ANALYSIS, 0.75, [], RiskLevel.NONE, {}, True)
        ]
        conf = self.reliability_engine.aggregate_confidence(outputs)
        failures = self.reliability_engine.get_failures(outputs)
        should_defer, reason = self.reliability_engine.should_defer(conf, [], failures, RiskLevel.CRITICAL)
        self.assertTrue(should_defer)
        self.assertIn("safety threshold (0.80)", reason)

    def test_logic_high_risk_allowed(self):
        """Verify that HIGH risk is allowed at 0.75 confidence (threshold is for CRITICAL)"""
        outputs = [
            AgentOutput(AgentType.SECURITY_ANALYSIS, 0.75, [], RiskLevel.HIGH, {}, True)
        ]
        conf = self.reliability_engine.aggregate_confidence(outputs)
        failures = self.reliability_engine.get_failures(outputs)
        should_defer, reason = self.reliability_engine.should_defer(conf, [], failures, RiskLevel.HIGH)
        self.assertFalse(should_defer)

if __name__ == "__main__":
    unittest.main()
