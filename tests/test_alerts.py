"""
Unit tests for agent/alerts.py:
- Verifies overdue commitment detection
- Verifies silent stakeholder detection (14+ days)
- Verifies legal review stall detection based on historical patterns
"""

import unittest
from unittest.mock import MagicMock, patch
from agent.alerts import scan_deal_for_alerts, scan_all_deals_for_alerts


class TestAlerts(unittest.TestCase):
    @patch("agent.alerts.recall_deal")
    def test_overdue_commitment_alert(self, mock_recall_deal):
        mock_recall_deal.return_value = [
            {"text": "Alex committed to deliver redline by 2026-10-28 for Horizon Telecom."}
        ]

        alerts = scan_deal_for_alerts(
            deal_id="horizon-telecom",
            company_name="Horizon Telecom",
            current_date="2026-11-06"
        )

        overdue_alerts = [a for a in alerts if a.alert_type == "overdue_commitment"]
        self.assertEqual(len(overdue_alerts), 1)
        self.assertEqual(overdue_alerts[0].severity, "CRITICAL")
        self.assertIn("2026-10-28", overdue_alerts[0].title)

    @patch("agent.alerts.recall_deal")
    def test_silent_stakeholder_alert(self, mock_recall_deal):
        mock_recall_deal.return_value = []
        interactions = [
            {"date": "2026-10-15", "type": "Call", "transcript": "Meeting with Claire Vance"}
        ]

        alerts = scan_deal_for_alerts(
            deal_id="summit-biotech",
            company_name="Summit BioTech",
            current_date="2026-11-06",
            interactions=interactions
        )

        silent_alerts = [a for a in alerts if a.alert_type == "silent_stakeholder"]
        self.assertEqual(len(silent_alerts), 1)
        self.assertGreaterEqual(int(silent_alerts[0].title.split()[3]), 14)

    @patch("agent.alerts.recall_deal")
    def test_stalled_legal_review_alert(self, mock_recall_deal):
        mock_recall_deal.return_value = []
        interactions = [
            {"date": "2026-10-18", "type": "Legal Submission", "transcript": "Submitted to Legal Review stage."}
        ]

        alerts = scan_deal_for_alerts(
            deal_id="horizon-telecom",
            company_name="Horizon Telecom",
            current_date="2026-11-06",
            interactions=interactions
        )

        stall_alerts = [a for a in alerts if a.alert_type == "stalled_stage"]
        self.assertEqual(len(stall_alerts), 1)
        self.assertEqual(stall_alerts[0].severity, "CRITICAL")
        self.assertIn("Titan Energy", stall_alerts[0].description)


if __name__ == "__main__":
    unittest.main()
