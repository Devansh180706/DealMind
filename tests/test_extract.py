"""
Unit tests for agent/extract.py:
- Verifies transcript extraction & JSON schema parsing
- Verifies duplicate detection using hash
- Verifies contradiction detection when budget changes
"""

import unittest
from unittest.mock import MagicMock, patch
from agent.extract import (
    extract_facts_from_transcript,
    compute_transcript_hash,
    _PROCESSED_HASHES,
    ExtractedTranscript,
    ObjectionItem,
    CommitmentItem,
    StakeholderItem,
)


class TestExtract(unittest.TestCase):
    def setUp(self):
        _PROCESSED_HASHES.clear()

    @patch("agent.extract.retain_deal_event")
    @patch("agent.extract.recall_deal")
    @patch("agent.extract.get_llm")
    def test_extract_facts_standard(self, mock_get_llm, mock_recall_deal, mock_retain_event):
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_recall_deal.return_value = []

        mock_llm.chat_json.return_value = ExtractedTranscript(
            summary="Discovery call with Sarah",
            stakeholders=[
                StakeholderItem(name="Sarah", role="CFO", sentiment="skeptical", concerns=["cost"])
            ],
            objections=[
                ObjectionItem(category="pricing", summary="$75k too high", raised_by="Sarah", severity="high")
            ],
            competitors_mentioned=["CloudFort"],
            pricing_discussed="$75,000",
            commitments=[
                CommitmentItem(action="Send ROI study", owner="Alex", due_date="2026-09-28")
            ],
            next_steps=["Send proposal"]
        )

        transcript = "Marcus introduced Sarah Connor who objected to $75k price tag."
        extracted, sentences, meta = extract_facts_from_transcript(
            transcript=transcript,
            deal_id="acme",
            company_name="Acme Corp",
            date="2026-09-22"
        )

        self.assertIsNotNone(extracted)
        self.assertEqual(meta["status"], "ingested")
        self.assertGreater(len(sentences), 4)
        self.assertTrue(any("Sarah (CFO at Acme Corp)" in s for s in sentences))
        self.assertTrue(any("Alex committed to: 'Send ROI study'" in s for s in sentences))
        self.assertEqual(mock_retain_event.call_count, len(sentences))

    @patch("agent.extract.retain_deal_event")
    @patch("agent.extract.recall_deal")
    @patch("agent.extract.get_llm")
    def test_duplicate_skipping(self, mock_get_llm, mock_recall_deal, mock_retain_event):
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_recall_deal.return_value = []
        mock_llm.chat_json.return_value = ExtractedTranscript(
            summary="Demo call",
            stakeholders=[],
            objections=[],
            competitors_mentioned=[],
            pricing_discussed=None,
            commitments=[],
            next_steps=[]
        )

        transcript = "Identical meeting transcript content."
        # First call: should ingest
        _, _, meta1 = extract_facts_from_transcript(
            transcript=transcript,
            deal_id="deal-1",
            company_name="Company 1",
            date="2026-10-01"
        )
        self.assertEqual(meta1["status"], "ingested")

        # Second call: should skip due to duplicate hash
        extracted2, sentences2, meta2 = extract_facts_from_transcript(
            transcript=transcript,
            deal_id="deal-1",
            company_name="Company 1",
            date="2026-10-01"
        )
        self.assertIsNone(extracted2)
        self.assertEqual(sentences2, [])
        self.assertEqual(meta2["status"], "skipped")
        self.assertEqual(meta2["reason"], "duplicate_hash")

    @patch("agent.extract.retain_deal_event")
    @patch("agent.extract.recall_deal")
    @patch("agent.extract.get_llm")
    def test_contradiction_detection(self, mock_get_llm, mock_recall_deal, mock_retain_event):
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        # Previous memory says budget was $120k
        mock_recall_deal.return_value = [
            {"id": "m1", "text": "Initial budget approved around $120,000 for enterprise license."}
        ]
        # Current call says budget updated to $90k
        mock_llm.chat_json.return_value = ExtractedTranscript(
            summary="Budget update call",
            stakeholders=[],
            objections=[],
            competitors_mentioned=[],
            pricing_discussed="$90,000 cap",
            commitments=[],
            next_steps=[]
        )

        transcript = "Procurement stated corporate slashed budget to $90k."
        _, sentences, meta = extract_facts_from_transcript(
            transcript=transcript,
            deal_id="deal-beacon",
            company_name="Beacon FinTech",
            date="2026-10-20"
        )

        self.assertTrue(meta["contradiction_detected"])
        self.assertTrue(any("UPDATE:" in s and "$90,000 cap" in s for s in sentences))


if __name__ == "__main__":
    unittest.main()

