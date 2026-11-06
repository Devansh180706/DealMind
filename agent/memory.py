"""
Memory wrapper around Vectorize Hindsight Client.
Strictly adheres to:
- Rule 1: Never invent Hindsight API parameters.
- Rule 2: Every Hindsight call goes through agent/memory.py only.

Bank layout:
- One bank per deal: 'deal-{deal_id}' (e.g. 'deal-acme-corp')
- One shared company bank: 'company-playbook'
"""

import os
import logging
from typing import Optional, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("agent.memory")

PLAYBOOK_BANK_ID = "company-playbook"


def _format_deal_bank_id(deal_id: str) -> str:
    """Format deal bank id consistently: deal-{cleaned_deal_id}."""
    clean_id = deal_id.strip().lower().replace(" ", "-").replace("_", "-")
    if not clean_id.startswith("deal-"):
        return f"deal-{clean_id}"
    return clean_id


class MemoryClient:
    """Singleton gateway to Vectorize Hindsight."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.base_url = (
            base_url or os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
        ).strip()
        self.api_key = (api_key or os.getenv("HINDSIGHT_API_KEY", "")).strip()

        if not self.api_key:
            logger.warning("HINDSIGHT_API_KEY is not set. Memory calls may fail.")

        from hindsight_client import Hindsight
        self.client = Hindsight(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=60.0
        )

    # -------------------------------------------------------------------------
    # Deal-Specific Operations
    # -------------------------------------------------------------------------

    def retain_deal_event(
        self,
        deal_id: str,
        text: str,
        date: Optional[str] = None,
        context: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """
        Retain a plain-English event sentence into the deal's isolated bank.
        """
        bank_id = _format_deal_bank_id(deal_id)
        meta = metadata or {}
        meta["deal_id"] = deal_id

        # Use ISO timestamp if provided
        timestamp_val: Optional[datetime] = None
        if date:
            try:
                # Handle YYYY-MM-DD or full ISO
                if len(date) == 10:
                    timestamp_val = datetime.strptime(date, "%Y-%m-%d")
                else:
                    timestamp_val = datetime.fromisoformat(date)
            except Exception as e:
                logger.debug(f"Could not parse timestamp '{date}': {e}")

        try:
            resp = self.client.retain(
                bank_id=bank_id,
                content=text,
                timestamp=timestamp_val,
                context=context,
                metadata=meta,
            )
            return bool(getattr(resp, "success", True))
        except Exception as e:
            logger.error(f"Failed to retain deal event into '{bank_id}': {e}")
            raise e

    def recall_deal(
        self,
        deal_id: str,
        question: str,
        max_tokens: int = 4096,
    ) -> list[dict[str, Any]]:
        """
        Recall atomic facts from a deal's isolated memory bank.
        Returns a list of dicts: [{'id': ..., 'text': ..., 'type': ..., 'occurred_start': ...}]
        """
        bank_id = _format_deal_bank_id(deal_id)
        try:
            resp = self.client.recall(
                bank_id=bank_id,
                query=question,
                max_tokens=max_tokens,
            )
            results = []
            for item in getattr(resp, "results", []):
                results.append({
                    "id": getattr(item, "id", None),
                    "text": getattr(item, "text", ""),
                    "type": getattr(item, "type", "world"),
                    "entities": getattr(item, "entities", []),
                    "context": getattr(item, "context", None),
                    "occurred_start": getattr(item, "occurred_start", None),
                    "metadata": getattr(item, "metadata", {}),
                })
            return results
        except Exception as e:
            logger.error(f"Failed to recall deal facts from '{bank_id}': {e}")
            # If bank is brand new and has no memories, return empty list gracefully
            if "not found" in str(e).lower() or "empty" in str(e).lower() or "404" in str(e):
                return []
            raise e

    # -------------------------------------------------------------------------
    # Shared Company Playbook Operations
    # -------------------------------------------------------------------------

    def retain_playbook(
        self,
        text: str,
        context: Optional[str] = "playbook",
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """
        Retain a win/loss retrospective or proven tactic into the shared company-playbook bank.
        """
        try:
            resp = self.client.retain(
                bank_id=PLAYBOOK_BANK_ID,
                content=text,
                context=context,
                metadata=metadata or {},
            )
            return bool(getattr(resp, "success", True))
        except Exception as e:
            logger.error(f"Failed to retain playbook item: {e}")
            raise e

    def recall_playbook(
        self,
        question: str,
        max_tokens: int = 4096,
    ) -> list[dict[str, Any]]:
        """
        Recall relevant historical playbooks and tactics matching the question.
        """
        try:
            resp = self.client.recall(
                bank_id=PLAYBOOK_BANK_ID,
                query=question,
                max_tokens=max_tokens,
            )
            results = []
            for item in getattr(resp, "results", []):
                results.append({
                    "id": getattr(item, "id", None),
                    "text": getattr(item, "text", ""),
                    "type": getattr(item, "type", "experience"),
                    "entities": getattr(item, "entities", []),
                    "occurred_start": getattr(item, "occurred_start", None),
                })
            return results
        except Exception as e:
            logger.error(f"Failed to recall from '{PLAYBOOK_BANK_ID}': {e}")
            if "not found" in str(e).lower() or "empty" in str(e).lower() or "404" in str(e):
                return []
            raise e

    def reflect_playbook(
        self,
        question: str,
        budget: str = "mid",
    ) -> str:
        """
        Execute an agentic reflection loop across all closed deal retrospectives
        in the company playbook bank.
        """
        try:
            resp = self.client.reflect(
                bank_id=PLAYBOOK_BANK_ID,
                query=question,
                budget=budget,
            )
            return getattr(resp, "text", "") or ""
        except Exception as e:
            logger.error(f"Failed to reflect on '{PLAYBOOK_BANK_ID}': {e}")
            raise e


# Global singleton instance
_memory_instance: Optional[MemoryClient] = None

def get_memory() -> MemoryClient:
    """Return initialized singleton MemoryClient."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = MemoryClient()
    return _memory_instance

# Direct module-level functions mapping to workflow specifications
def retain_deal_event(deal_id: str, text: str, date: Optional[str] = None, metadata: Optional[dict[str, str]] = None) -> bool:
    return get_memory().retain_deal_event(deal_id=deal_id, text=text, date=date, metadata=metadata)

def recall_deal(deal_id: str, question: str) -> list[dict[str, Any]]:
    return get_memory().recall_deal(deal_id=deal_id, question=question)

def retain_playbook(text: str, metadata: Optional[dict[str, str]] = None) -> bool:
    return get_memory().retain_playbook(text=text, metadata=metadata)

def recall_playbook(question: str) -> list[dict[str, Any]]:
    return get_memory().recall_playbook(question=question)

def reflect_playbook(question: str) -> str:
    return get_memory().reflect_playbook(question=question)

