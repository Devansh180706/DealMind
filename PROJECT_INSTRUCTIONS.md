# DealMind — Workspace Rules & Instructions

**PROJECT**: DealMind (Deal Intelligence Agent for HackwithHyderabad 3.0).  
**JUDGING CRITERIA**:
- Innovation: 30%
- Hindsight Memory: 25%
- Technical Implementation: 20%
- User Experience (UX): 15%
- Real-world Impact: 10%

**TECH STACK**:
- Python 3.11+
- Streamlit UI (`app.py`)
- Vectorize Hindsight (`hindsight-client`) for ALL persistent long-term memory (retain, recall, reflect)
- Groq API for ultra-fast LLM inference (Llama 3.3 / Qwen / Mistral with robust JSON validation and retries)
- Pydantic for strict JSON schema extraction and validation

**MANDATORY ARCHITECTURAL RULES**:
1. **Never invent Hindsight API parameters**. Read `docs/hindsight/` first. If unsure, verify or state clearly.
2. **Every Hindsight call goes through `agent/memory.py` only**. No direct client calls outside this module.
3. **Every LLM call goes through `agent/llm.py`**, which must retry with exponential backoff, validate JSON schemas, and fall back gracefully.
4. **Never hardcode secrets**. Read all keys from `.env`.
5. **Memory Grounding**: Any LLM output stating facts about a deal must cite the memory it originated from. If memory is empty, say "no history yet", never hallucinate.
6. **Tight Scope**:
   - Pre-call brief (with Memory ON/OFF comparison toggle)
   - Post-call debrief & extraction
   - Outcome learning loop & playbook reflection
   - Intelligent alerts (overdue promises, silent stakeholders, stalls)
7. **Code Quality**: Type hints, docstrings, and unit tests per module.
8. **Artifacts & Proof**: Maintain clear walk-throughs and test reports.

