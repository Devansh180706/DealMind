"""
End-to-End Verification Test Suite (Phase 4):
Tests the 5 mandatory edge cases from the workflow specification:
1. Smoke test of the full flow on one deal (extraction -> retention -> recall -> briefing)
2. Contradiction handling (explicit UPDATE generated when constraint changes)
3. Empty-memory behavior (MUST say 'no history yet', never guess/hallucinate)
4. Malformed LLM output (retry and repair loop)
5. Duplicate ingestion (SHA-256 deduplication)
"""

import unittest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel

from agent.extract import extract_facts_from_transcript, _PROCESSED_HASHES, ExtractedTranscript
from agent.brief import generate_pre_call_brief
from agent.llm import LLMClient


class MockSchema(BaseModel):
    title: str
    status: str


class TestVerificationSuite(unittest.TestCase):
    def setUp(self):
        _PROCESSED_HASHES.clear()

    # -------------------------------------------------------------------------
    # Test 1: Full Flow on One Deal
    # -------------------------------------------------------------------------
    @patch("agent.extract.retain_deal_event")
    @patch("agent.extract.recall_deal")
    @patch("agent.brief.recall_deal")
    @patch("agent.brief.recall_playbook")
    @patch("agent.extract.get_llm")
    @patch("agent.brief.get_llm")
    def test_01_full_flow_on_one_deal(
        self, mock_brief_llm, mock_ext_llm, mock_brief_recall_pb, mock_brief_recall_deal,
        mock_ext_recall_deal, mock_ext_retain
    ):
        """Simulate extracting notes, retaining facts, and generating pre-call brief."""
        # 1. Extraction step
        ext_client = MagicMock()
        mock_ext_llm.return_value = ext_client
        mock_ext_recall_deal.return_value = []
        ext_client.chat_json.return_value = ExtractedTranscript(
            summary="Kickoff call with Marcus Wright.",
            stakeholders=[],
            objections=[],
            competitors_mentioned=["CloudFort"],
            pricing_discussed="$75,000",
            commitments=[],
            next_steps=["Schedule CFO meeting"]
        )

        extracted, sentences, meta = extract_facts_from_transcript(
            transcript="Marcus confirmed $75k scope and mentioned CloudFort.",
            deal_id="acme-test",
            company_name="Acme Test",
            date="2026-10-10"
        )
        self.assertEqual(meta["status"], "ingested")
        self.assertGreater(len(sentences), 0)

        # 2. Briefing step
        brief_client = MagicMock()
        mock_brief_llm.return_value = brief_client
        brief_client.chat.return_value = "Executive Brief: Acme Test has $75k budget [Memory #1]."
        mock_brief_recall_deal.return_value = [
            {"id": "m1", "text": "Acme confirmed $75k scope", "occurred_start": "2026-10-10"}
        ]
        mock_brief_recall_pb.return_value = []

        brief = generate_pre_call_brief("acme-test", "Acme Test", memory_mode="ON")
        self.assertTrue(brief.has_history)
        self.assertIn("[Memory #1]", brief.brief_markdown)
        self.assertEqual(len(brief.memories_used), 1)

    # -------------------------------------------------------------------------
    # Test 2: Contradiction Handling
    # -------------------------------------------------------------------------
    @patch("agent.extract.retain_deal_event")
    @patch("agent.extract.recall_deal")
    @patch("agent.extract.get_llm")
    def test_02_contradiction_handling(self, mock_get_llm, mock_recall_deal, mock_retain_event):
        """Verifies contradiction detection creates an explicit UPDATE memory."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_recall_deal.return_value = [
            {"text": "On 2026-10-01, initial budget was approved at $120,000."}
        ]
        mock_llm.chat_json.return_value = ExtractedTranscript(
            summary="Procurement cut budget.",
            stakeholders=[],
            objections=[],
            competitors_mentioned=[],
            pricing_discussed="$90,000 maximum budget",
            commitments=[],
            next_steps=[]
        )

        _, sentences, meta = extract_facts_from_transcript(
            transcript="Budget slashed from $120k down to $90k.",
            deal_id="beacon-test",
            company_name="Beacon Test",
            date="2026-10-20"
        )
        self.assertTrue(meta["contradiction_detected"])
        update_sentences = [s for s in sentences if "UPDATE:" in s]
        self.assertEqual(len(update_sentences), 1)
        self.assertIn("$90,000 maximum budget", update_sentences[0])

    # -------------------------------------------------------------------------
    # Test 3: Empty-Memory Behavior
    # -------------------------------------------------------------------------
    @patch("agent.brief.recall_deal")
    def test_03_empty_memory_behavior(self, mock_recall_deal):
        """Rule 5: If memory is empty, MUST say 'no history yet', never guess."""
        mock_recall_deal.return_value = []

        brief = generate_pre_call_brief("empty-deal-xyz", "Ghost Co", memory_mode="ON")
        self.assertFalse(brief.has_history)
        self.assertIn("no history yet", brief.brief_markdown.lower())
        self.assertEqual(len(brief.memories_used), 0)

    # -------------------------------------------------------------------------
    # Test 4: Malformed LLM Output
    # -------------------------------------------------------------------------
    def test_04_malformed_llm_output_recovery(self):
        """Verifies that the LLM client handles malformed JSON and reprompts."""
        client = LLMClient(api_key="mock_key")
        # Simulate invalid JSON followed by valid JSON
        client.chat = MagicMock(side_effect=[
            'Invalid { JSON string ...',
            '{"title": "Fixed Deal", "status": "active"}'
        ])

        obj = client.chat_json(
            messages=[{"role": "user", "content": "test"}],
            schema=MockSchema,
            max_repairs=3
        )
        self.assertEqual(obj.title, "Fixed Deal")
        self.assertEqual(obj.status, "active")
        self.assertEqual(client.chat.call_count, 2)

    # -------------------------------------------------------------------------
    # Test 5: Duplicate Ingestion
    # -------------------------------------------------------------------------
    @patch("agent.extract.retain_deal_event")
    @patch("agent.extract.recall_deal")
    @patch("agent.extract.get_llm")
    def test_05_duplicate_ingestion(self, mock_get_llm, mock_recall_deal, mock_retain_event):
        """Verifies identical transcripts are skipped using SHA-256 hash."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_recall_deal.return_value = []
        mock_llm.chat_json.return_value = ExtractedTranscript(
            summary="First call",
            stakeholders=[],
            objections=[],
            competitors_mentioned=[],
            pricing_discussed=None,
            commitments=[],
            next_steps=[]
        )

        sample_text = "This is a recurring transcript test content."
        # Call 1: Ingested
        _, _, meta1 = extract_facts_from_transcript(sample_text, "deal-x", "Company X", "2026-10-01")
        self.assertEqual(meta1["status"], "ingested")

        # Call 2: Skipped as duplicate
        _, _, meta2 = extract_facts_from_transcript(sample_text, "deal-x", "Company X", "2026-10-01")
        self.assertEqual(meta2["status"], "skipped")
        self.assertEqual(meta2["reason"], "duplicate_hash")


if __name__ == "__main__":
    unittest.main()
