"""
Pre-call briefing engine with Memory ON / Memory OFF modes.
Strictly adheres to:
- Rule 5: State facts must cite the memory they came from. If memory is empty, say "no history yet", never guess.
- Pre-call brief with multi-vector recall (objections, stakeholders, commitments, competitors, last contact, playbook).
"""

import logging
from typing import Optional, Any
from pydantic import BaseModel, Field
from agent.llm import get_llm
from agent.memory import recall_deal, recall_playbook

logger = logging.getLogger("agent.brief")


class PreCallBriefResult(BaseModel):
    deal_id: str
    company_name: str
    memory_mode: str  # "ON" or "OFF"
    brief_markdown: str
    memories_used: list[dict[str, Any]] = Field(default_factory=list)
    has_history: bool = True


def generate_pre_call_brief(
    deal_id: str,
    company_name: str,
    memory_mode: str = "ON",
) -> PreCallBriefResult:
    """
    Generate an executive pre-call brief for a sales rep.
    - If memory_mode == "OFF": generates generic boilerplate without recall.
    - If memory_mode == "ON": queries 5 memory vectors + playbook, cites facts,
      or returns 'no history yet' if memory bank is empty.
    """
    llm = get_llm()

    # -------------------------------------------------------------------------
    # Mode OFF: Pure generic LLM generation (No memory recall)
    # -------------------------------------------------------------------------
    if memory_mode.upper() == "OFF":
        prompt = (
            f"You are a sales advisor. Provide pre-call preparation advice for a rep meeting with '{company_name}'.\n"
            "Note: You have NO specific background memory or past notes for this account.\n"
            "Provide general best practices: agenda, active listening, rapport building."
        )
        response_text = llm.chat(
            messages=[
                {"role": "system", "content": "You are a generic sales assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return PreCallBriefResult(
            deal_id=deal_id,
            company_name=company_name,
            memory_mode="OFF",
            brief_markdown=response_text,
            memories_used=[],
            has_history=False
        )

    # -------------------------------------------------------------------------
    # Mode ON: Multi-vector recall across Deal Bank + Company Playbook
    # -------------------------------------------------------------------------
    raw_memories: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    queries = [
        "What objections, budget constraints, or pricing concerns were raised?",
        "Who are the key stakeholders, what are their roles and sentiments?",
        "What promises, commitments, and deadlines were agreed upon?",
        "Which competitors were mentioned and what was discussed?",
        "What happened in the most recent interaction summary?"
    ]

    for q in queries:
        facts = recall_deal(deal_id, q)
        for f in facts:
            fid = f.get("id") or f.get("text")
            if fid not in seen_ids:
                seen_ids.add(fid)
                raw_memories.append(f)

    # Empty memory guardrail (Workflow Rule 5)
    if not raw_memories:
        return PreCallBriefResult(
            deal_id=deal_id,
            company_name=company_name,
            memory_mode="ON",
            brief_markdown=(
                f"### Pre-Call Brief for {company_name}\n\n"
                "**No history yet.**\n\n"
                "There are no recorded interactions or memories in Hindsight for this deal yet. "
                "Log a call transcript or meeting notes to initialize the deal intelligence profile."
            ),
            memories_used=[],
            has_history=False
        )

    # Recall relevant winning tactics from company-playbook
    playbook_facts = recall_playbook("How to handle pricing objections or competitors?")

    # Format memories with explicit citations: [Memory #1], [Memory #2]
    context_lines = []
    memories_used_list = []

    for idx, mem in enumerate(raw_memories, start=1):
        citation = f"[Memory #{idx}]"
        text = mem.get("text", "")
        occurred = mem.get("occurred_start") or "Unknown date"
        context_lines.append(f"{citation} (Date: {occurred}): {text}")
        memories_used_list.append({
            "citation": citation,
            "id": mem.get("id", f"mem-{idx}"),
            "text": text,
            "date": occurred,
            "type": mem.get("type", "world"),
            "source": "deal_bank"
        })

    playbook_context_lines = []
    for idx, pb in enumerate(playbook_facts, start=1):
        pb_citation = f"[Playbook #{idx}]"
        pb_text = pb.get("text", "")
        playbook_context_lines.append(f"{pb_citation}: {pb_text}")
        memories_used_list.append({
            "citation": pb_citation,
            "id": pb.get("id", f"pb-{idx}"),
            "text": pb_text,
            "date": "Historical",
            "type": "playbook",
            "source": "company_playbook"
        })

    deal_context_str = "\n".join(context_lines)
    playbook_context_str = "\n".join(playbook_context_lines) if playbook_context_lines else "No specific playbook entries found."

    prompt = (
        f"You are the Deal Intelligence Agent preparing a sales rep for an upcoming meeting with {company_name} (Deal ID: {deal_id}).\n\n"
        f"RECALLED DEAL MEMORIES (CITE THESE USING [Memory #X]):\n{deal_context_str}\n\n"
        f"RECALLED COMPANY PLAYBOOK TACTICS (CITE THESE USING [Playbook #Y]):\n{playbook_context_str}\n\n"
        "INSTRUCTIONS:\n"
        "1. Write a sharp, high-impact executive pre-call brief in markdown.\n"
        "2. Structure into:\n"
        "   - **Account Snapshot & Stage**\n"
        "   - **Key Stakeholders & Sentiment Analysis** (cite quotes/facts with [Memory #X])\n"
        "   - **Open Objections & Competitor Threats** (cite [Memory #X])\n"
        "   - **Recommended Winning Playbook Tactic** (grounded in [Playbook #Y])\n"
        "   - **Overdue & Pending Commitments** (flag promises with deadlines)\n"
        "   - **Recommended Call Agenda & Opening Hook**\n"
        "3. CRITICAL RULE: Every statement of fact must cite its source tag (e.g. [Memory #1]). If a detail is not in memory, do not guess or fabricate."
    )

    brief_text = llm.chat(
        messages=[
            {"role": "system", "content": "You are an elite B2B sales deal intelligence assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return PreCallBriefResult(
        deal_id=deal_id,
        company_name=company_name,
        memory_mode="ON",
        brief_markdown=brief_text,
        memories_used=memories_used_list,
        has_history=True
    )
