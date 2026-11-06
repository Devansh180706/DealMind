# DealMind — Specification (SPEC.md)

**Project Name:** DealMind (Deal Intelligence Agent)  
**Hackathon:** HackwithHyderabad 3.0 (Hindsight Memory Hackathon)  
**Track:** Sales & Revenue Copilot  

---

## 1. User Persona
- **Role:** Alex, Senior Account Executive (AE) at CloudScale (B2B SaaS).
- **Context:** Alex manages 15–20 high-stakes enterprise sales pipelines simultaneously ($25k–$150k ACV).
- **Pain Points:** 
  - Enterprise deals drag across 3–6 months with 4–8 meetings per deal.
  - Key information (CFO objections, legal blockers, discount caps, promised features) gets lost in 30-page CRM notes.
  - Reps walk into critical renewal or closing calls unprepared, repeating previously answered questions or stumbling on previously addressed objections.
  - No cross-deal visibility: Lessons learned from won/lost deals in the team stay trapped in individual heads.

---

## 2. The 3 Core Flows

### Flow 1: Pre-Call Briefing (The "Brief Me" Superpower)
- **Input:** Rep selects a deal ID (e.g. `deal-acme-corp`).
- **Memory Query:** Queries the deal's Hindsight memory bank (`deal-{deal_id}`) across 5 vectors:
  1. Open objections & status
  2. Stakeholders, roles, and sentiment history
  3. Unfulfilled promises and upcoming commitments
  4. Competitor mentions & battlecard counter-arguments
  5. Last interaction summary
  - *Plus:* Queries the shared `company-playbook` memory bank for proven tactics that worked in similar deal stages.
- **Output:** A structured, scannable pre-call brief.
- **The "Memory Switch" (Demo Feature):**
  - **Memory ON:** Hyper-specific brief citing exact quotes, dated commitments, and past objections with citation tags.
  - **Memory OFF:** Generic, boilerplate advice (proving the immense value of persistent memory).

### Flow 2: Post-Call Debrief & Smart Memory Extraction
- **Input:** Raw notes or meeting transcript pasted into the agent.
- **Processing:**
  1. Fast LLM parsing (Groq) into structured JSON schema (objections, pricing details, stakeholder sentiment, commitments with due dates).
  2. Entity resolution & plain-English memory sentence generation (e.g. *"On 2026-10-15, CFO Sarah Connor objected to the $45k price tag, requesting an ROI breakdown."*).
  3. Contradiction & change detection: Recalls previous related facts before retaining to detect changes (e.g., budget updated from $50k to $35k). Retains updates explicitly.
  4. Deduplication: SHA-256 content hashing prevents duplicate ingestion.
  5. Long-term storage: Calls Hindsight `retain()` on the deal's bank.

### Flow 3: Cross-Deal Playbook Learning Loop
- **Trigger:** Deal stage updated to `Closed Won` or `Closed Lost`.
- **Processing:**
  1. Synthesizes deal retrospective (key objections encountered, turning points, tactics that worked or failed).
  2. Retains the retrospective into the shared `company-playbook` memory bank.
  3. Triggers Hindsight `reflect()` across all closed deals to discover cross-deal patterns (e.g., *"Deals with CFO pricing pushback close 80% more often when an ROI calculator is sent within 48 hours"*).

---

## 3. The 60-Second Demo Script (for Judges)

| Time | Action on Screen | Narrative |
|---|---|---|
| **00:00 - 00:15** | Open **Deal List** in Streamlit. Show "Acme Corp" highlighted in Red with an Alert badge. | *"Alex has a closing call with Acme Corp in 10 minutes. The agent flags: 'CFO silent for 14 days; $45k budget objection open.' The rep hasn't looked at notes in 2 weeks."* |
| **00:15 - 00:30** | Go to **Brief Me**. Click **Memory OFF** toggle first. | *"Without memory, any generic LLM gives boilerplate advice like 'Be polite and listen carefully.' Completely useless for enterprise sales."* |
| **00:30 - 00:45** | Toggle **Memory ON**. | *"Now watch Hindsight memory activate. It recalls Sarah Connor's exact budget objection from Oct 12, warns about Competitor Alpha's discount pitch, and pulls the winning tactic from our shared Playbook."* |
| **00:45 - 00:55** | Go to **Log a Call**. Paste brief transcript of today's call where Alex shared the ROI case study and won the deal. Mark as Closed Won. | *"Alex executes the playbook and wins the deal. The agent extracts commitments, updates the stage, and retains the win into the company playbook."* |
| **00:55 - 01:00** | Switch to **Playbook Insights**. Click "Reflect on Tactics". | *"Hindsight autonomously runs reflection across all deals and proves our thesis: ROI case studies overcome CFO pricing objections across 8 out of 10 deals. The agent gets smarter after every call."* |

---

## 4. What "Memory Visibly Helping" Looks Like on Screen
1. **Memories Used Sidebar / Drawer:** Every factual claim in the brief includes an interactive badge (e.g., `[Memory #F-102: Call 2026-10-12]`). Clicking it shows the exact source memory sentence.
2. **Side-by-Side Comparison (A/B Test View):** Instant toggle between "With Hindsight Memory" and "Without Memory".
3. **Contradiction Tracker:** Visual diff when a customer updates their constraints (e.g., `Old: $50,000` ➔ `New: $35,000`).
4. **Empty Memory Guardrail:** When a deal is brand new, the agent states *"No history yet"* rather than hallucinating facts.

---

## 5. Explicitly Out of Scope
- Real-time audio recording or speech-to-text (relies on text transcript/call notes input).
- Direct Salesforce/HubSpot OAuth sync (uses clean internal JSON data).
- Complex user permission/multi-tenant billing tiers.

