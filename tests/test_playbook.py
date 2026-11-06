"""
Unit tests for agent/playbook.py:
- Verifies record_deal_closure_and_learn retaining and reflecting
- Verifies verify_against_ground_truth pattern matching
"""

import unittest
from unittest.mock import MagicMock, patch
from agent.playbook import record_deal_closure_and_learn, verify_against_ground_truth


class TestPlaybook(unittest.TestCase):
    @patch("agent.playbook.reflect_playbook")
    @patch("agent.playbook.retain_playbook")
    def test_record_deal_closure(self, mock_retain_pb, mock_reflect_pb):
        mock_retain_pb.return_value = True
        mock_reflect_pb.return_value = "ROI case studies improve win rates on price objections."

        res = record_deal_closure_and_learn(
            deal_id="deal-acme",
            company_name="Acme Corp",
            outcome="Closed Won",
            deal_size="$75k",
            key_objection="$75k budget objection",
            decisive_tactic="Delivered 3-year ROI model",
            notes="CFO approved immediately after ROI presentation."
        )

        self.assertEqual(res["status"], "recorded")
        self.assertIn("Acme Corp", res["retrospective_retained"])
        self.assertIn("ROI case studies", res["reflection_insights"])
        mock_retain_pb.assert_called_once()
        mock_reflect_pb.assert_called_once()

    @patch("agent.playbook.get_current_learned_insights")
    def test_verify_against_ground_truth(self, mock_get_insights):
        mock_get_insights.return_value = (
            "1. ROI Case Studies: Presenting an ROI case study helps close CFO pricing objections.\n"
            "2. Legal Stalls: Deals stalled in legal review for >14 days risk slipping."
        )

        res = verify_against_ground_truth()
        self.assertIn("discovery_rate", res)
        self.assertGreaterEqual(res["patterns_discovered"], 2)


if __name__ == "__main__":
    unittest.main()

