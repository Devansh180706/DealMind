"""
DealMind — Deal Intelligence Agent | Streamlit Web Application
5 Core Views:
1. 📊 Deal Pipeline (with risk badges & metrics)
2. ⚡ Brief Me (with Memory ON/OFF comparison toggle & Memories Used citations drawer)
3. 📝 Log a Call (live transcript extraction, contradiction detection, & memory retention)
4. 🚨 Active Alerts (overdue commitments, silent stakeholders, legal stalls)
5. 🧠 Playbook Insights (cross-deal learning powered by Hindsight reflect & Ground Truth validation)
"""

import os
import json
import html
from pathlib import Path
from datetime import datetime
import streamlit as st

from agent.brief import generate_pre_call_brief
from agent.extract import extract_facts_from_transcript
from agent.alerts import scan_all_deals_for_alerts, scan_deal_for_alerts
from agent.playbook import get_current_learned_insights, record_deal_closure_and_learn, verify_against_ground_truth
from agent.memory import recall_deal, recall_playbook

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="DealMind | Deal Intelligence Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).resolve().parent / "data" / "synthetic" / "deals.json"

@st.cache_data
def load_deals():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

deals    = load_deals()
deal_map = {d["deal_id"]: d for d in deals}
open_deals = [d for d in deals if d.get("status") == "Open"]
won_deals  = [d for d in deals if d.get("status") == "Closed Won"]
lost_deals = [d for d in deals if d.get("status") == "Closed Lost"]

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header  { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-header   { font-size: 1.05rem; color: #64748B; margin-bottom: 1.5rem; }
    .metric-card  { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; }
    .memory-badge { background-color: #EEF2FF; border: 1px solid #C7D2FE; color: #3730A3;
                    padding: 2px 8px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar — branding only (no nav radio) ───────────────────────────────────
st.sidebar.image("https://img.icons8.com/isometric/100/brain.png", width=64)
st.sidebar.title("DealMind")
st.sidebar.caption("Autonomous Deal Intelligence • Powered by Hindsight & Groq")
st.sidebar.divider()
st.sidebar.markdown("**HackwithHyderabad 3.0**")
st.sidebar.info(
    "💡 **Judging Spotlight**: Click **'⚡ Brief Me'** and toggle **Memory ON vs. OFF** "
    "to witness Hindsight memory transform generic advice into precision deal intelligence."
)

# ── Top-level tab navigation ─────────────────────────────────────────────────
tab_pipeline, tab_brief, tab_log, tab_alerts, tab_playbook = st.tabs([
    "📊 Deal Pipeline",
    "⚡ Brief Me",
    "📝 Log a Call",
    "🚨 Active Alerts",
    "🧠 Playbook Insights",
])


# =============================================================================
# 1. DEAL PIPELINE
# =============================================================================
with tab_pipeline:
    st.markdown('<div class="main-header">Deal Pipeline & Intelligence Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Active accounts monitored across isolated Hindsight memory banks.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    total_val = sum(
        int(d["deal_size"].replace("$", "").replace(",", ""))
        for d in deals if "deal_size" in d
    )
    c1.metric("Monitored Pipeline", f"${total_val:,}")
    c2.metric("Open Active Deals",  len(open_deals))
    c3.metric("Closed Won",         len(won_deals))
    c4.metric("Closed Lost",        len(lost_deals))

    st.markdown("---")

    for d in deals:
        status = d.get("status", "Open")
        with st.expander(f"{d['company_name']} ({d['deal_size']}) — Stage: {status}"):
            cols = st.columns([2, 2, 2])
            cols[0].markdown(f"**Industry:** {d.get('industry', 'N/A')}")
            cols[0].markdown(f"**Competitor:** {d.get('competitor', 'None')}")
            cols[1].markdown(f"**Memory Bank:** `deal-{d['deal_id']}`")
            cols[1].markdown(f"**Close Date:** {d.get('close_date', 'Pending')}")
            sh_list = [f"{s['name']} ({s['role']})" for s in d.get("key_stakeholders", [])]
            cols[2].markdown(f"**Stakeholders:** {', '.join(sh_list)}")
            st.markdown(f"**Total Logged Interactions:** {len(d.get('interactions', []))}")


# =============================================================================
# 2. BRIEF ME (THE HERO DEMO FEATURE)
# =============================================================================
with tab_brief:
    st.markdown('<div class="main-header">⚡ Pre-Call Briefing (Copilot)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Executive preparation grounded in Hindsight persistent memory.</div>',
        unsafe_allow_html=True
    )

    selected_deal_id = st.selectbox(
        "Select Deal Account to Brief:",
        options=list(deal_map.keys()),
        format_func=lambda x: f"{deal_map[x]['company_name']} ({deal_map[x]['deal_size']} — {deal_map[x]['status']})"
    )
    deal_obj = deal_map[selected_deal_id]

    col_btn, col_toggle = st.columns([2, 3])
    with col_toggle:
        memory_mode = st.radio(
            "🧠 Hindsight Memory Mode:",
            ["ON (Grounded in Deal Bank & Playbook)", "OFF (Generic LLM Baseline)"],
            horizontal=True,
            help="Toggle between Memory ON and Memory OFF to verify Hindsight memory impact."
        )
        mode_val = "ON" if "ON" in memory_mode else "OFF"

    if st.button("Generate Pre-Call Brief", type="primary"):
        with st.spinner("Querying Hindsight memory banks and synthesizing brief..."):
            brief_res = generate_pre_call_brief(
                deal_id=selected_deal_id,
                company_name=deal_obj["company_name"],
                memory_mode=mode_val,
            )

        left_col, right_col = st.columns([3, 2])

        with left_col:
            if mode_val == "ON":
                st.success("✅ Brief successfully grounded in Vectorize Hindsight memory!")
            else:
                st.warning("⚠️ Memory is OFF: Advice is purely generic.")
            st.markdown(brief_res.brief_markdown)

        with right_col:
            st.markdown("### 📚 Memories Used & Citations")
            st.caption(f"Bank: `deal-{selected_deal_id}` + `company-playbook`")

            if brief_res.memories_used:
                for mem in brief_res.memories_used:
                    with st.container():
                        st.markdown(
                            f"<span class='memory-badge'>{mem.get('citation')}</span> "
                            f"<small>Date: {mem.get('date', 'N/A')}</small>",
                            unsafe_allow_html=True
                        )
                        st.markdown(f"> *\"{mem.get('text')}\"*")
            else:
                st.info("No memories queried (Memory Mode is OFF or bank empty).")


# =============================================================================
# 3. LOG A CALL & LIVE EXTRACTION
# =============================================================================
with tab_log:
    st.markdown('<div class="main-header">📝 Log a Call & Extract Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Paste meeting transcripts or notes. Automatically extracts structured facts, '
        'detects contradictions, and retains into Hindsight.</div>',
        unsafe_allow_html=True
    )

    selected_deal = st.selectbox(
        "Select Deal:",
        options=list(deal_map.keys()),
        format_func=lambda x: f"{deal_map[x]['company_name']} ({deal_map[x]['deal_id']})"
    )
    deal_info = deal_map[selected_deal]

    c_date, c_type = st.columns(2)
    interaction_date = c_date.date_input("Meeting Date", datetime(2026, 11, 6)).strftime("%Y-%m-%d")
    interaction_type = c_type.selectbox(
        "Interaction Type",
        ["Discovery Call", "Demo & Pricing", "Executive Review", "Negotiation", "Email Check-in"]
    )

    sample_default = (
        "Marcus Wright and CFO Sarah Connor joined today. Sarah stated their budget is strictly $75k. "
        "Alex committed to email the customized ROI case study by Friday. CloudFort was mentioned."
    )
    transcript_input = st.text_area(
        "Meeting Notes / Transcript:",
        value=sample_default,
        height=150,
        placeholder="Paste transcript or debrief notes here..."
    )

    if st.button("Extract Facts & Retain into Hindsight", type="primary"):
        with st.spinner("Extracting structured facts and updating memory..."):
            extracted, sentences, meta = extract_facts_from_transcript(
                transcript=transcript_input,
                deal_id=selected_deal,
                company_name=deal_info["company_name"],
                date=interaction_date
            )

        if meta.get("status") == "skipped":
            st.warning("⚠️ Duplicate transcript detected via SHA-256 hash. Skipped duplicate ingestion.")
        else:
            st.success(f"🎉 Successfully ingested and retained {len(sentences)} memory facts into bank `deal-{selected_deal}`!")

            col_ext, col_mem = st.columns(2)

            with col_ext:
                st.markdown("#### 🔍 Extracted Structured JSON")
                if extracted:
                    st.json(extracted.model_dump())

            with col_mem:
                st.markdown("#### 🧠 Plain-English Memories Retained")
                if meta.get("contradiction_detected"):
                    st.error("⚡ Contradiction / Budget Change Detected & Recorded!")
                for s in sentences:
                    st.markdown(f"- {s}")


# =============================================================================
# 4. ACTIVE ALERTS  — uses Streamlit-native components (no raw HTML injection)
# =============================================================================
with tab_alerts:
    st.markdown('<div class="main-header">🚨 Proactive Deal Risk Alerts</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Continuous scanning of Hindsight memory for overdue commitments, '
        'silent champions, and stage stalls.</div>',
        unsafe_allow_html=True
    )

    with st.spinner("Scanning all deal memory banks for risks..."):
        all_alerts = scan_all_deals_for_alerts(deals, current_date="2026-11-06")

    crit_count = sum(1 for a in all_alerts if a.severity == "CRITICAL")
    high_count = sum(1 for a in all_alerts if a.severity == "HIGH")

    a1, a2, a3 = st.columns(3)
    a1.metric("Total Active Alerts", len(all_alerts))
    a2.metric("Critical Blockers",   crit_count)
    a3.metric("High Risks",          high_count)

    st.markdown("---")

    if not all_alerts:
        st.success("✅ No active risk alerts found across all deal accounts.")
    else:
        for alert in all_alerts:
            is_critical = alert.severity == "CRITICAL"
            icon  = "🔴" if is_critical else "🟡"
            label = f"{icon} **[{alert.severity}]  {alert.company_name} — {alert.title}**"

            with st.expander(label, expanded=is_critical):
                # Description banner
                if is_critical:
                    st.error(str(alert.description))
                else:
                    st.warning(str(alert.description))

                # Evidence from memory
                st.markdown("**🧠 Evidence from Memory:**")
                st.caption(str(alert.evidence_memory))

                # Recommended action
                st.info(f"**💡 Recommended Action:** {alert.suggested_action}")


# =============================================================================
# 5. PLAYBOOK INSIGHTS (CROSS-DEAL LEARNING)
# =============================================================================
with tab_playbook:
    st.markdown('<div class="main-header">🧠 Autonomous Playbook Insights</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Cross-deal reflection powered by Hindsight reflect() and Ground Truth validation.</div>',
        unsafe_allow_html=True
    )

    sub_insights, sub_eval, sub_close = st.tabs([
        "💡 Learned Intelligence",
        "🎯 Ground Truth Verification",
        "🏆 Close Deal & Learn",
    ])

    with sub_insights:
        st.markdown("### Cross-Deal Playbook (Synthesized by Hindsight `reflect()`)")
        if st.button("🔄 Refresh Playbook Reflection", type="secondary"):
            st.cache_data.clear()
        insights = get_current_learned_insights()
        st.info(insights)

    with sub_eval:
        st.markdown("### Ground Truth Pattern Discovery")
        st.caption("Verifies whether the agent independently discovered the planted patterns in the synthetic dataset.")

        eval_res = verify_against_ground_truth()
        if "error" in eval_res:
            st.error(eval_res["error"])
        else:
            e1, e2 = st.columns(2)
            e1.metric("Patterns Discovered", f"{eval_res['patterns_discovered']} / {eval_res['total_patterns']}")
            e2.metric("Discovery Rate", eval_res["discovery_rate"])

            st.markdown("#### Discovered Pattern Breakdown:")
            for item in eval_res.get("evaluations", []):
                icon = "✅" if item["discovered_by_agent"] else "❌"
                st.markdown(f"**{icon} {item['pattern_name']}**")
                st.markdown(f"- *Evidence deals:* {', '.join(item['evidence_deals'])}")
                st.markdown(f"- *Winning/Preventive action:* {item['expected_insight']}")
                st.markdown("---")

    with sub_close:
        st.markdown("### Record Deal Outcome to Trigger Learning Loop")
        if not open_deals:
            st.info("No open deals remaining to close.")
        else:
            with st.form("close_deal_form"):
                deal_to_close = st.selectbox(
                    "Select Open Deal to Close:",
                    options=[d["deal_id"] for d in open_deals],
                    format_func=lambda x: f"{deal_map[x]['company_name']} ({deal_map[x].get('deal_size', 'N/A')})"
                )
                deal_info_close = deal_map.get(deal_to_close, {})
                deal_name       = deal_info_close.get("company_name", "")
                outcome_val     = st.radio("Outcome", ["Closed Won", "Closed Lost"], horizontal=True)
                deal_val        = st.text_input("Deal Value", value=deal_info_close.get("deal_size", "$75,000"))
                objection_text  = st.text_input("Key Objection Overcome / Faced", value="Pricing pushback from CFO")
                tactic_text     = st.text_input("Decisive Tactic Applied", value="Provided 3-year ROI breakdown and customer reference")
                notes_val       = st.text_area("Debrief Notes", value="CFO signed contract immediately following ROI proof presentation.")

                submitted = st.form_submit_button("Record Retrospective & Trigger Hindsight Reflect", type="primary")
                if submitted and deal_to_close:
                    with st.spinner("Recording retrospective to company-playbook and reflecting..."):
                        record_res = record_deal_closure_and_learn(
                            deal_id=deal_to_close,
                            company_name=deal_name,
                            outcome=outcome_val,
                            deal_size=deal_val,
                            key_objection=objection_text,
                            decisive_tactic=tactic_text,
                            notes=notes_val
                        )
                    st.success("🎉 Deal Retrospective retained to company-playbook!")
                    st.markdown("#### New Synthesized Playbook Reflection:")
                    st.write(record_res["reflection_insights"])
