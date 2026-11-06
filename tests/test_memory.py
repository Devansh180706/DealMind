"""
Unit tests for agent/memory.py:
- Verifies bank name formatting
- Verifies retain_deal_event call shapes and parameters
- Verifies recall_deal parsing
- Verifies playbook operations and reflect
"""

import unittest
from unittest.mock import MagicMock, patch
from agent.memory import (
    MemoryClient,
    _format_deal_bank_id,
    retain_deal_event,
    recall_deal,
    retain_playbook,
    reflect_playbook,
)


class TestMemoryWrapper(unittest.TestCase):
    def test_bank_id_formatting(self):
        self.assertEqual(_format_deal_bank_id("acme"), "deal-acme")
        self.assertEqual(_format_deal_bank_id("deal-acme"), "deal-acme")
        self.assertEqual(_format_deal_bank_id("Nexus Health"), "deal-nexus-health")
        self.assertEqual(_format_deal_bank_id("DEAL_GLOBAL_101"), "deal-global-101")

    @patch("hindsight_client.Hindsight")
    def test_retain_deal_event(self, mock_hindsight_cls):
        mock_instance = MagicMock()
        mock_hindsight_cls.return_value = mock_instance
        mock_instance.retain.return_value = MagicMock(success=True)

        mem = MemoryClient(api_key="mock_key")
        result = mem.retain_deal_event(
            deal_id="acme",
            text="CFO raised price objection",
            date="2026-10-15"
        )
        self.assertTrue(result)
        mock_instance.retain.assert_called_once()
        kwargs = mock_instance.retain.call_args.kwargs
        self.assertEqual(kwargs["bank_id"], "deal-acme")
        self.assertEqual(kwargs["content"], "CFO raised price objection")

    @patch("hindsight_client.Hindsight")
    def test_recall_deal_parsing(self, mock_hindsight_cls):
        mock_instance = MagicMock()
        mock_hindsight_cls.return_value = mock_instance

        mock_item = MagicMock()
        mock_item.id = "f-123"
        mock_item.text = "Budget was reduced to $35k"
        mock_item.type = "world"
        mock_item.entities = [{"name": "CFO"}]
        mock_item.occurred_start = "2026-10-15"
        mock_item.metadata = {"deal_id": "acme"}

        mock_instance.recall.return_value = MagicMock(results=[mock_item])

        mem = MemoryClient(api_key="mock_key")
        results = mem.recall_deal(deal_id="acme", question="What was the budget?")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "f-123")
        self.assertEqual(results[0]["text"], "Budget was reduced to $35k")
        self.assertEqual(results[0]["type"], "world")

    @patch("hindsight_client.Hindsight")
    def test_reflect_playbook(self, mock_hindsight_cls):
        mock_instance = MagicMock()
        mock_hindsight_cls.return_value = mock_instance
        mock_instance.reflect.return_value = MagicMock(
            text="ROI case studies close 80% of CFO pricing objections."
        )

        mem = MemoryClient(api_key="mock_key")
        reflection = mem.reflect_playbook(question="How to beat CFO pricing pushback?")
        self.assertIn("ROI case studies", reflection)
        mock_instance.reflect.assert_called_once()
        self.assertEqual(mock_instance.reflect.call_args.kwargs["bank_id"], "company-playbook")


if __name__ == "__main__":
    unittest.main()
