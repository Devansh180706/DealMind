"""
Unit tests for agent/brief.py:
- Verifies Memory ON vs Memory OFF modes
- Verifies empty memory guardrail ('no history yet')
- Verifies citation tracking in memories_used
"""

import unittest
from unittest.mock import MagicMock, patch
from agent.brief import generate_pre_call_brief


class TestBrief(unittest.TestCase):
    @patch("agent.brief.get_llm")
    def test_memory_mode_off(self, mock_get_llm):
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_llm.chat.return_value = "Generic sales advice: listen carefully and build rapport."

        res = generate_pre_call_brief(
            deal_id="acme",
            company_name="Acme Corp",
            memory_mode="OFF"
        )
        self.assertEqual(res.memory_mode, "OFF")
        self.assertEqual(len(res.memories_used), 0)
        self.assertIn("Generic sales advice", res.brief_markdown)
        self.assertFalse(res.has_history)

    @patch("agent.brief.recall_deal")
    def test_empty_memory_guardrail(self, mock_recall_deal):
        mock_recall_deal.return_value = []

        res = generate_pre_call_brief(
            deal_id="brand-new-deal",
            company_name="New Co",
            memory_mode="ON"
        )
        self.assertEqual(res.memory_mode, "ON")
        self.assertFalse(res.has_history)
        self.assertIn("No history yet", res.brief_markdown)
        self.assertEqual(len(res.memories_used), 0)

    @patch("agent.brief.recall_playbook")
    @patch("agent.brief.recall_deal")
    @patch("agent.brief.get_llm")
    def test_memory_mode_on_with_facts(self, mock_get_llm, mock_recall_deal, mock_recall_playbook):
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_llm.chat.return_value = (
            "### Brief\n"
            "Sarah Connor objected to $75k price tag [Memory #1].\n"
            "Use ROI calculator tactic [Playbook #1]."
        )

        mock_recall_deal.return_value = [
            {"id": "m-1", "text": "Sarah Connor objected to $75k", "occurred_start": "2026-09-22", "type": "world"}
        ]
        mock_recall_playbook.return_value = [
            {"id": "pb-1", "text": "Sending ROI calculators resolves CFO price objections 80% of the time."}
        ]

        res = generate_pre_call_brief(
            deal_id="acme",
            company_name="Acme Corp",
            memory_mode="ON"
        )
        self.assertEqual(res.memory_mode, "ON")
        self.assertTrue(res.has_history)
        self.assertGreater(len(res.memories_used), 0)
        self.assertIn("[Memory #1]", res.brief_markdown)


if __name__ == "__main__":
    unittest.main()
