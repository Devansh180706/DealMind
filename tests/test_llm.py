"""
Tests for agent/llm.py:
- Malformed JSON recovery and repair logic
- Schema validation with Pydantic
- Retry simulation
"""

import unittest
from unittest.mock import MagicMock
from pydantic import BaseModel
from agent.llm import LLMClient


class DemoSchema(BaseModel):
    summary: str
    score: int


class TestLLMClient(unittest.TestCase):
    def test_chat_json_success(self):
        """Verify chat_json correctly parses clean JSON."""
        client = LLMClient(api_key="mock_key")
        client.chat = MagicMock(return_value='{"summary": "Deal looking strong", "score": 85}')

        result = client.chat_json(
            messages=[{"role": "user", "content": "analyze deal"}],
            schema=DemoSchema
        )
        self.assertEqual(result.summary, "Deal looking strong")
        self.assertEqual(result.score, 85)

    def test_chat_json_markdown_wrapped(self):
        """Verify chat_json strips markdown code blocks."""
        client = LLMClient(api_key="mock_key")
        client.chat = MagicMock(return_value='```json\n{"summary": "Wrapped in markdown", "score": 90}\n```')

        result = client.chat_json(
            messages=[{"role": "user", "content": "analyze"}],
            schema=DemoSchema
        )
        self.assertEqual(result.summary, "Wrapped in markdown")
        self.assertEqual(result.score, 90)

    def test_chat_json_repairs_malformed_json(self):
        """Verify chat_json re-prompts on malformed JSON and succeeds on repair."""
        client = LLMClient(api_key="mock_key")
        # First response is broken JSON, second response is fixed
        client.chat = MagicMock(side_effect=[
            '{"summary": "Broken syntax...',  # Malformed
            '{"summary": "Fixed syntax", "score": 100}'  # Fixed
        ])

        result = client.chat_json(
            messages=[{"role": "user", "content": "analyze"}],
            schema=DemoSchema,
            max_repairs=3
        )
        self.assertEqual(result.summary, "Fixed syntax")
        self.assertEqual(result.score, 100)
        self.assertEqual(client.chat.call_count, 2)

    def test_chat_json_raises_on_persistent_failure(self):
        """Verify chat_json raises ValueError if repairs are exhausted."""
        client = LLMClient(api_key="mock_key")
        client.chat = MagicMock(return_value='Not a json string at all')

        with self.assertRaises(ValueError) as ctx:
            client.chat_json(
                messages=[{"role": "user", "content": "analyze"}],
                schema=DemoSchema,
                max_repairs=2
            )
        self.assertIn("Failed to obtain valid JSON", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
