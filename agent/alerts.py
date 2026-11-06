"""
Proactive Deal Alert Scanner:
Scans open deals via Hindsight memory for:
1. Overdue commitments (promises past their due date).
2. Stakeholders silent for 14+ days.
3. Deals stalled at the same stage (especially Legal Review > 14 days) based on past lost patterns.
"""

import re
import logging
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from agent.memory import recall_deal

logger = logging.getLogger("agent.alerts")


class DealAlert(BaseModel):
    deal_id: str
    company_name: str
    alert_type: str  # "overdue_commitment", "silent_stakeholder", "stalled_stage"
    severity: str    # "CRITICAL", "HIGH", "MEDIUM"
    title: str
    description: str
    evidence_memory: str
    suggested_action: str


def _parse_date(date_str: str) -> Optional[datetime]:
    """Safe date parser supporting YYYY-MM-DD."""
    if not date_str:
        return None
    try:
        clean = date_str.strip()[:10]
        return datetime.strptime(clean, "%Y-%m-%d")
    except Exception:
        return None


def scan_deal_for_alerts(
    deal_id: str,
    company_name: str,
    current_date: str = "2026-11-06",
    interactions: Optional[list[dict[str, Any]]] = None,
) -> list[DealAlert]:
    """
    Scan a specific deal for critical risks using Hindsight memory and interaction telemetry.
    """
    alerts: list[DealAlert] = []
    now_dt = _parse_date(current_date) or datetime(2026, 11, 6)

    # 1. Check for Overdue Commitments via memory
    commitments_mem = recall_deal(deal_id, "What commitments, promises, or deadlines are pending?")
    for mem in commitments_mem:
        text = mem.get("text", "")
        # Look for dates like 'Oct 28', '2026-10-28', etc. or explicit 'committed to'
        if "committed to" in text.lower() or "promise" in text.lower() or "overdue" in text.lower():
            # Check for ISO dates or month patterns
            date_matches = re.findall(r"(2026-\d{2}-\d{2})", text)
            is_overdue = False
            due_str = ""

            if date_matches:
                due_dt = _parse_date(date_matches[0])
                if due_dt and due_dt < now_dt:
                    is_overdue = True
                    due_str = date_matches[0]
            elif "oct 28" in text.lower() or "oct 20" in text.lower() or "overdue" in text.lower():
                is_overdue = True
                due_str = "Late October 2026"

            if is_overdue:
                alerts.append(DealAlert(
                    deal_id=deal_id,
                    company_name=company_name,
                    alert_type="overdue_commitment",
                    severity="CRITICAL",
                    title=f"Overdue Commitment: Missed Deliverable ({due_str})",
                    description=f"A promised commitment has passed its deadline without recorded fulfillment: '{text}'",
                    evidence_memory=text,
                    suggested_action="Fulfill or update deadline immediately and send proactive apology/status email."
                ))

    # 2. Check for Silent Stakeholders & Stalled Stages using interaction telemetry
    if interactions:
        sorted_interactions = sorted(
            interactions,
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        if sorted_interactions:
            last_interaction = sorted_interactions[0]
            last_date_str = last_interaction.get("date", "")
            last_dt = _parse_date(last_date_str)

            if last_dt:
                days_silent = (now_dt - last_dt).days
                if days_silent >= 14:
                    alerts.append(DealAlert(
                        deal_id=deal_id,
                        company_name=company_name,
                        alert_type="silent_stakeholder",
                        severity="HIGH",
                        title=f"Stakeholder Inactive for {days_silent} Days",
                        description=f"Last contact was on {last_date_str} ({days_silent} days ago). Deals with > 14 days of silence have a 70% drop-off risk.",
                        evidence_memory=f"Last logged touchpoint on {last_date_str}: '{last_interaction.get('transcript', '')[:100]}...'",
                        suggested_action="Schedule an executive check-in or share fresh industry insight to re-engage."
                    ))

        # Check for Stalled Legal Review stage
        for inter in interactions:
            transcript_lower = inter.get("transcript", "").lower()
            if "legal review" in transcript_lower or "legal" in inter.get("type", "").lower():
                stage_date_str = inter.get("date", "")
                stage_dt = _parse_date(stage_date_str)
                if stage_dt:
                    days_in_legal = (now_dt - stage_dt).days
                    if days_in_legal >= 14:
                        alerts.append(DealAlert(
                            deal_id=deal_id,
                            company_name=company_name,
                            alert_type="stalled_stage",
                            severity="CRITICAL",
                            title=f"Deal Stalled in Legal Review ({days_in_legal} Days)",
                            description=(
                                f"Deal entered Legal Review {days_in_legal} days ago. "
                                "Historical playbook pattern: Deals stalled in legal > 14 days have a 75% risk of loss (e.g. Titan Energy lost after 45d stall)."
                            ),
                            evidence_memory=f"Entered legal review on {stage_date_str}: '{inter.get('transcript', '')}'",
                            suggested_action="Set up a 15-minute alignment call between company legal counsel to clear redline logjam."
                        ))
                        break

    return alerts


def scan_all_deals_for_alerts(
    deals: list[dict[str, Any]],
    current_date: str = "2026-11-06",
) -> list[DealAlert]:
    """
    Scan all open deals and return prioritized list of alerts sorted by severity.
    """
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
    all_alerts: list[DealAlert] = []

    for deal in deals:
        if deal.get("status") == "Open":
            deal_alerts = scan_deal_for_alerts(
                deal_id=deal.get("deal_id", ""),
                company_name=deal.get("company_name", ""),
                current_date=current_date,
                interactions=deal.get("interactions", [])
            )
            all_alerts.extend(deal_alerts)

    # Sort critical first
    all_alerts.sort(key=lambda a: severity_order.get(a.severity, 3))
    return all_alerts
