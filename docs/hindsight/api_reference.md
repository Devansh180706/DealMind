# Hindsight API Reference (Python Client)

`hindsight-client` is the official Python SDK for Vectorize Hindsight, a long-term memory engine for AI agents that extracts entities, relationships, and temporal facts into a knowledge graph.

## Installation

```bash
pip install hindsight-client
```

## Initialization

```python
import os
from hindsight_client import Hindsight

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io"),
    api_key=os.getenv("HINDSIGHT_API_KEY")
)
```

## Core Operations

### 1. Retain (`retain`)
Stores unstructured text into a specific memory bank. Hindsight extracts entities, facts, relationships, and timestamps automatically.

```python
response = client.retain(
    bank_id="deal-acme-corp",
    content="On 2026-10-15, Sarah Connor (CFO at Acme Corp) raised a budget objection stating their FY27 budget is capped at $45,000.",
    context="objection", # optional context category
    metadata={"deal_id": "deal-acme-corp", "stage": "negotiation"} # optional metadata
)
```

### 2. Recall (`recall`)
Queries the memory bank for structured atomic facts using multi-strategy search (BM25 keyword search, vector semantic search, temporal recency, and knowledge graph traversal).

```python
recall_result = client.recall(
    bank_id="deal-acme-corp",
    query="What budget concerns did the CFO raise?"
)

# Iterating results:
for item in recall_result.results:
    print(item.text)
    # item attributes include: .text, .type, .entities, .occurred_start
```

### 3. Reflect (`reflect`)
Executes an agentic reasoning loop over the memory bank to synthesize insights, find cross-deal patterns, and generate high-level conclusions.

```python
reflection = client.reflect(
    bank_id="company-playbook",
    query="What objection-handling tactics have the highest win rate against Competitor X when pricing is challenged?"
)
print(reflection.text)
```

## Memory Bank Architecture for Deal Intelligence Agent

1. **Per-Deal Banks**: `deal-{deal_id}` (e.g., `deal-acme-101`)
   - Stores chronological interactions, objections, stakeholder sentiment, pricing constraints, commitments, and stage transitions for a specific customer deal.
2. **Company Playbook Bank**: `company-playbook`
   - Stores cross-deal learnings, closed-won/closed-lost retrospectives, proven objection rebuttals, and winning playbooks across the sales team.

