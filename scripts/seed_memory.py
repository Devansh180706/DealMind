"""
Seed Memory Script:
Loads synthetic deals from data/synthetic/deals.json,
extracts and retains all chronological interaction facts into each deal's isolated bank,
and retains retrospectives into the company-playbook bank.
Ensures the live demo and Streamlit UI have rich, realistic memory ready out of the box!
"""

import os
import sys
import json
from pathlib import Path

# Ensure root directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.memory import retain_deal_event, retain_playbook, reflect_playbook

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "synthetic" / "deals.json"


def seed():
    if not DATA_FILE.exists():
        print(f"Error: {DATA_FILE} does not exist. Run scripts/generate_data.py first.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        deals = json.load(f)

    print(f"\n============================================================")
    print(f"SEEDING HINDSIGHT MEMORY WITH {len(deals)} B2B SAAS DEALS")
    print(f"============================================================\n")

    total_memories_retained = 0
    total_retrospectives = 0

    for idx, deal in enumerate(deals, start=1):
        deal_id = deal["deal_id"]
        company = deal["company_name"]
        status = deal["status"]
        size = deal.get("deal_size", "N/A")
        print(f"[{idx}/{len(deals)}] Seeding deal: {company} ({deal_id}) | Stage: {status} | Value: {size}")

        # Retain each interaction
        for inter in deal.get("interactions", []):
            date = inter.get("date", "2026-10-01")
            itype = inter.get("type", "Interaction")
            transcript = inter.get("transcript", "")

            # Formulate clear memory sentence
            memory_sentence = (
                f"On {date}, during {itype} with {company} ({deal_id}): {transcript}"
            )
            retain_deal_event(
                deal_id=deal_id,
                text=memory_sentence,
                date=date,
                metadata={"type": itype, "company": company}
            )
            total_memories_retained += 1

        # If deal is closed, retain retrospective into company-playbook
        if status in ["Closed Won", "Closed Lost"]:
            close_date = deal.get("close_date", "2026-10-25")
            last_interaction = deal.get("interactions", [])[-1]["transcript"] if deal.get("interactions") else ""
            
            retro_sentence = (
                f"RETROSPECTIVE: Deal {company} ({deal_id}, size: {size}) ended as {status} on {close_date}. "
                f"Competitor faced: {deal.get('competitor', 'Unknown')}. Outcome summary: {last_interaction}"
            )
            retain_playbook(
                text=retro_sentence,
                metadata={"deal_id": deal_id, "status": status, "size": size}
            )
            total_retrospectives += 1

    print(f"\nSeeding complete!")
    print(f"  - Total Deal Memories Retained: {total_memories_retained}")
    print(f"  - Total Playbook Retrospectives Retained: {total_retrospectives}")

    print("\nTriggering Hindsight reflect() over company-playbook...")
    try:
        reflection = reflect_playbook("What are the primary reasons we win or lose deals when pricing is challenged?")
        print(f"Hindsight Reflection Result:\n{reflection[:300]}...\n")
    except Exception as e:
        print(f"Note: Reflection call: {e}")

    print("=" * 60)
    print("MEMORY SEEDING FINISHED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    seed()
