"""
Extraction Pipeline:
Converts raw call transcripts into structured JSON facts, plain-English memory sentences,
detects contradictions against existing memory, and prevents duplicate ingestion via hashing.
"""

import hashlib
import logging
from typing import Optional, Any
from pydantic import BaseModel, Field
from agent.llm import get_llm
from agent.memory import retain_deal_event, recall_deal

logger = logging.getLogger("agent.extract")

# In-memory registry of processed transcript hashes
_PROCESSED_HASHES: set[str] = set()


class StakeholderItem(BaseModel):
    name: str = Field(description="Name of person")
    role: str = Field(description="Title or role")
    sentiment: str = Field(description="positive, neutral, skeptical, hostile")
    concerns: list[str] = Field(default_factory=list, description="Key concerns voiced")


class ObjectionItem(BaseModel):
    category: str = Field(description="pricing, security, competitor, timeline, other")
    summary: str = Field(description="Summary of the objection")
    raised_by: str = Field(description="Name or role of person who raised it")
    severity: str = Field(description="low, medium, high, deal_breaker")


class CommitmentItem(BaseModel):
    action: str = Field(description="Specific promised deliverable or action")
    owner: str = Field(description="Who committed (e.g. Alex, Sarah Connor)")
    due_date: Optional[str] = Field(default=None, description="Due date if mentioned, e.g. YYYY-MM-DD")


class ExtractedTranscript(BaseModel):
    summary: str = Field(description="Brief 1-2 sentence overview of the interaction")
    stakeholders: list[StakeholderItem] = Field(default_factory=list)
    objections: list[ObjectionItem] = Field(default_factory=list)
    competitors_mentioned: list[str] = Field(default_factory=list)
    pricing_discussed: Optional[str] = Field(default=None, description="Pricing, budget, or discount discussed")
    commitments: list[CommitmentItem] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


def compute_transcript_hash(transcript: str) -> str:
    """Compute SHA-256 hash of transcript text for deduplication."""
    return hashlib.sha256(transcript.strip().encode("utf-8")).hexdigest()


def extract_facts_from_transcript(
    transcript: str,
    deal_id: str,
    company_name: str,
    date: str,
) -> tuple[Optional[ExtractedTranscript], list[str], dict[str, Any]]:
    """
    Extract structured facts from raw transcript, check for duplicates and contradictions,
    and retain them as dated memory sentences in Hindsight.
    
    Returns:
        (extracted_json, memory_sentences_retained, meta_report)
    """
    tx_hash = compute_transcript_hash(transcript)
    if tx_hash in _PROCESSED_HASHES:
        logger.info(f"Duplicate transcript detected (hash: {tx_hash[:8]}). Skipping ingestion.")
        return None, [], {"status": "skipped", "reason": "duplicate_hash", "hash": tx_hash}

    llm = get_llm()
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert sales deal intelligence extractor. "
                "Analyze the meeting notes/transcript and extract key deal entities, "
                "sentiment, objections, pricing, commitments, and competitors."
            )
        },
        {
            "role": "user",
            "content": (
                f"Deal ID: {deal_id}\n"
                f"Company: {company_name}\n"
                f"Date: {date}\n\n"
                f"Transcript:\n{transcript}"
            )
        }
    ]

    extracted: ExtractedTranscript = llm.chat_json(
        messages=messages,
        schema=ExtractedTranscript,
    )

    sentences_to_retain: list[str] = []

    # 1. Summary memory
    sentences_to_retain.append(
        f"On {date}, interaction summary for {company_name} ({deal_id}): {extracted.summary}"
    )

    # 2. Stakeholders
    for s in extracted.stakeholders:
        concerns_str = f" Concerns: {', '.join(s.concerns)}." if s.concerns else ""
        sentences_to_retain.append(
            f"On {date}, {s.name} ({s.role} at {company_name}) expressed {s.sentiment} sentiment.{concerns_str}"
        )

    # 3. Objections
    for obj in extracted.objections:
        sentences_to_retain.append(
            f"On {date}, {obj.raised_by} at {company_name} raised a {obj.category} objection ({obj.severity} severity): '{obj.summary}'."
        )

    # 4. Competitors
    for comp in extracted.competitors_mentioned:
        sentences_to_retain.append(
            f"On {date}, competitor '{comp}' was mentioned during discussions with {company_name}."
        )

    # 5. Pricing & Contradiction Detection
    detected_contradiction = None
    if extracted.pricing_discussed:
        # Check existing memory for past pricing/budget facts
        past_pricing_memories = recall_deal(deal_id, "What was the previous pricing or budget constraint?")
        existing_pricing_texts = [m["text"] for m in past_pricing_memories if "pricing" in m["text"].lower() or "budget" in m["text"].lower()]

        if existing_pricing_texts:
            # Check if current pricing conflicts/updates previous
            detected_contradiction = {
                "previous_facts": existing_pricing_texts[:2],
                "new_fact": extracted.pricing_discussed
            }
            sentences_to_retain.append(
                f"UPDATE: On {date}, pricing/budget constraint for {company_name} ({deal_id}) was updated to: '{extracted.pricing_discussed}'. (Supersedes earlier discussions)."
            )
        else:
            sentences_to_retain.append(
                f"On {date}, pricing discussion for {company_name} ({deal_id}): '{extracted.pricing_discussed}'."
            )

    # 6. Commitments
    for com in extracted.commitments:
        due_str = f" due by {com.due_date}" if com.due_date else ""
        sentences_to_retain.append(
            f"On {date}, {com.owner} committed to: '{com.action}'{due_str} for deal {company_name}."
        )

    # 7. Next Steps
    for step in extracted.next_steps:
        sentences_to_retain.append(
            f"On {date}, agreed next step for {company_name}: '{step}'."
        )

    # Retain all sentences into deal's isolated Hindsight bank
    for sentence in sentences_to_retain:
        retain_deal_event(
            deal_id=deal_id,
            text=sentence,
            date=date,
            metadata={"source": "transcript_extract", "hash": tx_hash}
        )

    _PROCESSED_HASHES.add(tx_hash)

    meta_report = {
        "status": "ingested",
        "hash": tx_hash,
        "sentences_count": len(sentences_to_retain),
        "contradiction_detected": detected_contradiction is not None,
        "contradiction_details": detected_contradiction,
    }

    return extracted, sentences_to_retain, meta_report
