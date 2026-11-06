"""
Synthetic Data Generator for Deal Intelligence Agent.
Produces:
1. data/synthetic/deals.json: 10 realistic B2B SaaS deals (6 closed: 4 won, 2 lost; 4 open)
   Each with 4-8 dated interactions (transcripts/notes), stakeholders, pricing, competitors.
2. data/synthetic/ground_truth.json: Planted patterns for cross-deal validation.
"""

import os
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEALS = [
    {
        "deal_id": "acme-corp",
        "company_name": "Acme Corporation",
        "industry": "Manufacturing Tech",
        "deal_size": "$75,000",
        "status": "Closed Won",
        "close_date": "2026-10-25",
        "competitor": "CloudFort",
        "key_stakeholders": [
            {"name": "Sarah Connor", "role": "CFO", "initial_sentiment": "skeptical"},
            {"name": "Marcus Wright", "role": "VP Engineering", "initial_sentiment": "positive"}
        ],
        "interactions": [
            {
                "interaction_id": "acme-int-1",
                "date": "2026-09-10",
                "type": "Discovery Call",
                "transcript": "Marcus Wright (VP Eng at Acme) loves the security telemetry features. Mentioned they are also looking at CloudFort. Current budget approved around $80k. Next step: demo with CFO."
            },
            {
                "interaction_id": "acme-int-2",
                "date": "2026-09-22",
                "type": "Demo & Objection Call",
                "transcript": "Sarah Connor (CFO at Acme) joined. Sarah raised a severe budget objection: '$75k is too steep when CloudFort offered $55k.' She questioned our payback period. Alex promised to prepare a customized ROI financial model by Sept 28."
            },
            {
                "interaction_id": "acme-int-3",
                "date": "2026-09-28",
                "type": "Email Follow-up",
                "transcript": "Alex sent Sarah Connor the 3-year ROI case study showing a 310% return and 4-month payback period based on peer manufacturing benchmarks. Sarah responded positively and asked for legal review terms."
            },
            {
                "interaction_id": "acme-int-4",
                "date": "2026-10-12",
                "type": "Legal Review",
                "transcript": "Acme Legal requested standard DPA and security SLA. No major redlines. Alex delivered the signed compliance docs within 48 hours."
            },
            {
                "interaction_id": "acme-int-5",
                "date": "2026-10-25",
                "type": "Closing Call",
                "transcript": "Sarah Connor signed the 3-year contract for $75k ARR. Sarah noted that the ROI breakdown completely eliminated board resistance against CloudFort's lower bid."
            }
        ]
    },
    {
        "deal_id": "nexus-health",
        "company_name": "Nexus Health",
        "industry": "Healthcare AI",
        "deal_size": "$120,000",
        "status": "Closed Won",
        "close_date": "2026-10-18",
        "competitor": "CyberShield",
        "key_stakeholders": [
            {"name": "Dr. Rachel Green", "role": "Chief Medical Officer", "initial_sentiment": "positive"},
            {"name": "David Wallace", "role": "CFO", "initial_sentiment": "skeptical"}
        ],
        "interactions": [
            {
                "interaction_id": "nexus-int-1",
                "date": "2026-08-15",
                "type": "Initial Demo",
                "transcript": "Dr. Rachel Green praised the patient privacy safeguards. Mentioned CyberShield pitched them at a 20% discount. Next step: executive review with David Wallace (CFO)."
            },
            {
                "interaction_id": "nexus-int-2",
                "date": "2026-08-30",
                "type": "Pricing Call",
                "transcript": "David Wallace (CFO at Nexus) pushed hard on pricing: 'Healthcare margins are shrinking; we cannot justify $120k without clear cost-offset proofs.' David requested proof of cost savings."
            },
            {
                "interaction_id": "nexus-int-3",
                "date": "2026-09-05",
                "type": "ROI Briefing",
                "transcript": "Alex presented an ROI case study highlighting $420k in annual clinician time savings at hospital partner General Health. David Wallace remarked: 'This ROI calculator makes the $120k fee easily defensible to our trustees.'"
            },
            {
                "interaction_id": "nexus-int-4",
                "date": "2026-09-20",
                "type": "Security & Compliance Check",
                "transcript": "Nexus InfoSec reviewed HIPAA compliance certificates. Passed audit cleanly."
            },
            {
                "interaction_id": "nexus-int-5",
                "date": "2026-10-18",
                "type": "Closing",
                "transcript": "Contract executed at $120k ARR. Beat out CyberShield due to superior ROI validation and compliance transparency."
            }
        ]
    },
    {
        "deal_id": "vanguard-logistics",
        "company_name": "Vanguard Logistics",
        "industry": "Supply Chain",
        "deal_size": "$50,000",
        "status": "Closed Won",
        "close_date": "2026-09-14",
        "competitor": "DataTrace",
        "key_stakeholders": [
            {"name": "Elena Rostova", "role": "VP Operations", "initial_sentiment": "neutral"},
            {"name": "Thomas Sterling", "role": "Finance Director", "initial_sentiment": "hostile"}
        ],
        "interactions": [
            {
                "interaction_id": "vg-int-1",
                "date": "2026-07-20",
                "type": "Discovery",
                "transcript": "Elena Rostova outlined tracking delays costing them thousands daily. DataTrace is competing for the contract."
            },
            {
                "interaction_id": "vg-int-2",
                "date": "2026-08-04",
                "type": "Executive Pitch",
                "transcript": "Thomas Sterling (Finance Director) objected aggressively: 'Our logistics software budget is frozen at $35k. $50k is out of the question.' Alex committed to sharing a fleet optimization ROI breakdown by Aug 10."
            },
            {
                "interaction_id": "vg-int-3",
                "date": "2026-08-11",
                "type": "ROI Presentation",
                "transcript": "Alex delivered the fleet ROI analysis showing $140k saved in reduced route idle time. Thomas conceded the investment pays for itself within 90 days."
            },
            {
                "interaction_id": "vg-int-4",
                "date": "2026-09-14",
                "type": "Contract Signing",
                "transcript": "Thomas Sterling and Elena signed agreement for $50k. Decisive factor was the quantified ROI spreadsheet proving net annual cost reduction."
            }
        ]
    },
    {
        "deal_id": "apex-retail",
        "company_name": "Apex Retail Group",
        "industry": "E-Commerce",
        "deal_size": "$95,000",
        "status": "Closed Won",
        "close_date": "2026-10-02",
        "competitor": "CloudFort",
        "key_stakeholders": [
            {"name": "Chloe Bennett", "role": "Head of Digital", "initial_sentiment": "positive"},
            {"name": "Vikram Patel", "role": "Chief Architect", "initial_sentiment": "skeptical"}
        ],
        "interactions": [
            {
                "interaction_id": "apex-int-1",
                "date": "2026-08-10",
                "type": "Tech Scoping",
                "transcript": "Vikram Patel challenged API latency and Black Friday scale durability. CloudFort claiming sub-10ms."
            },
            {
                "interaction_id": "apex-int-2",
                "date": "2026-08-25",
                "type": "Architecture Proof",
                "transcript": "Alex conducted load test showing 4.2ms latency at 50,000 req/sec. Vikram approved technical criteria."
            },
            {
                "interaction_id": "apex-int-3",
                "date": "2026-09-15",
                "type": "Commercial Review",
                "transcript": "Pricing agreed at $95k. Alex provided SOC2 Type II audit report for compliance clearance."
            },
            {
                "interaction_id": "apex-int-4",
                "date": "2026-10-02",
                "type": "Signing",
                "transcript": "Deal Closed Won. Technical speed and fast audit proofs neutralized competitor."
            }
        ]
    },
    {
        "deal_id": "omni-finance",
        "company_name": "Omni Finance Corp",
        "industry": "Banking & FinTech",
        "deal_size": "$110,000",
        "status": "Closed Lost",
        "close_date": "2026-09-30",
        "competitor": "CloudFort",
        "key_stakeholders": [
            {"name": "Arthur Pendelton", "role": "CFO", "initial_sentiment": "skeptical"},
            {"name": "Lisa Ray", "role": "VP Operations", "initial_sentiment": "positive"}
        ],
        "interactions": [
            {
                "interaction_id": "omni-int-1",
                "date": "2026-08-01",
                "type": "Discovery",
                "transcript": "Lisa Ray requested automated audit logs. Stated budget is flexible around $100k-$120k."
            },
            {
                "interaction_id": "omni-int-2",
                "date": "2026-08-20",
                "type": "CFO Meeting",
                "transcript": "Arthur Pendelton (CFO) objected strongly to the $110k quote: 'CloudFort is offering their enterprise package for $80k. Why should we pay you $30k more?' Rep did NOT provide an ROI case study, instead offering a superficial 5% discount."
            },
            {
                "interaction_id": "omni-int-3",
                "date": "2026-09-12",
                "type": "Follow-up",
                "transcript": "Alex followed up asking for another call. Arthur replied: 'Without clear justification for the price difference over CloudFort, we cannot approve this.'"
            },
            {
                "interaction_id": "omni-int-4",
                "date": "2026-09-30",
                "type": "Lost Notice",
                "transcript": "Arthur notified us they signed with CloudFort for $80k. Deal Closed Lost. Key failure: inability to justify price premium with business ROI metrics."
            }
        ]
    },
    {
        "deal_id": "titan-energy",
        "company_name": "Titan Energy",
        "industry": "Renewables & Utilities",
        "deal_size": "$80,000",
        "status": "Closed Lost",
        "close_date": "2026-10-15",
        "competitor": "CyberShield",
        "key_stakeholders": [
            {"name": "Gordon Vance", "role": "Director IT", "initial_sentiment": "positive"},
            {"name": "Helena Cruz", "role": "General Counsel", "initial_sentiment": "neutral"}
        ],
        "interactions": [
            {
                "interaction_id": "titan-int-1",
                "date": "2026-07-15",
                "type": "Demo",
                "transcript": "Gordon Vance loved the platform. Fast evaluation. Budget approved at $80k."
            },
            {
                "interaction_id": "titan-int-2",
                "date": "2026-08-05",
                "type": "Legal Submission",
                "transcript": "Sent master services agreement to Helena Cruz (General Counsel). Deal entered Legal Review."
            },
            {
                "interaction_id": "titan-int-3",
                "date": "2026-08-25",
                "type": "Legal Follow-up",
                "transcript": "20 days in Legal Review. Helena Cruz flagged unlimited liability clause. No response from legal team for 3 weeks."
            },
            {
                "interaction_id": "titan-int-4",
                "date": "2026-09-20",
                "type": "Stall Check",
                "transcript": "Deal has now been stalled in Legal Review for 45 days. Gordon Vance silent. Priorities shifted to annual regulatory audit."
            },
            {
                "interaction_id": "titan-int-5",
                "date": "2026-10-15",
                "type": "Dead Deal",
                "transcript": "Gordon emailed to cancel procurement. Project budget lapsed due to the 2-month legal stalemate. Deal Closed Lost due to legal review stall."
            }
        ]
    },
    {
        "deal_id": "horizon-telecom",
        "company_name": "Horizon Telecom",
        "industry": "Telecommunications",
        "deal_size": "$65,000",
        "status": "Open",
        "close_date": "2026-11-30",
        "competitor": "CyberShield",
        "key_stakeholders": [
            {"name": "Devin Clark", "role": "Infrastructure Director", "initial_sentiment": "positive"},
            {"name": "Brenda Walsh", "role": "Senior Legal Counsel", "initial_sentiment": "neutral"}
        ],
        "interactions": [
            {
                "interaction_id": "hor-int-1",
                "date": "2026-10-01",
                "type": "Technical Validation",
                "transcript": "Devin Clark completed proof of concept. Selected us over CyberShield. Contract drafted for $65k."
            },
            {
                "interaction_id": "hor-int-2",
                "date": "2026-10-18",
                "type": "Submitted to Legal",
                "transcript": "Alex submitted contract to Brenda Walsh (Senior Legal Counsel). Stage set to Legal Review."
            },
            {
                "interaction_id": "hor-int-3",
                "date": "2026-10-25",
                "type": "Legal Redline Promise",
                "transcript": "Alex promised Brenda Walsh: 'Alex will deliver the mutual indemnification redline contract by Oct 28.' (OVERDUE COMMITMENT)."
            },
            {
                "interaction_id": "hor-int-4",
                "date": "2026-11-05",
                "type": "Risk Status",
                "transcript": "Deal has been stuck in Legal Review for 18 days with no update. Overdue promise to Brenda remains unfulfilled. High risk of stalling like Titan Energy."
            }
        ]
    },
    {
        "deal_id": "stellar-ai",
        "company_name": "Stellar AI Labs",
        "industry": "Artificial Intelligence",
        "deal_size": "$140,000",
        "status": "Open",
        "close_date": "2026-12-15",
        "competitor": "CloudFort",
        "key_stakeholders": [
            {"name": "Michael Chang", "role": "CFO", "initial_sentiment": "skeptical"},
            {"name": "Dr. Aris Thorne", "role": "VP AI Research", "initial_sentiment": "positive"}
        ],
        "interactions": [
            {
                "interaction_id": "stl-int-1",
                "date": "2026-10-10",
                "type": "Discovery",
                "transcript": "Dr. Aris Thorne needs high-speed indexing for LLM memory. Stated CloudFort is pitching $100k."
            },
            {
                "interaction_id": "stl-int-2",
                "date": "2026-10-22",
                "type": "Pricing Discussion",
                "transcript": "Michael Chang (CFO at Stellar AI) raised a severe objection: '$140k is $40k above our allocated Q4 tooling reserve. Why shouldn't we choose CloudFort at $100k?' Open objection pending financial justification."
            },
            {
                "interaction_id": "stl-int-3",
                "date": "2026-11-02",
                "type": "Follow-up",
                "transcript": "Alex scheduled a meeting for next week to address Michael Chang's price objection. Opportunity to apply the proven ROI playbook!"
            }
        ]
    },
    {
        "deal_id": "summit-biotech",
        "company_name": "Summit BioTech",
        "industry": "Life Sciences",
        "deal_size": "$45,000",
        "status": "Open",
        "close_date": "2026-12-01",
        "competitor": "DataTrace",
        "key_stakeholders": [
            {"name": "Claire Vance", "role": "VP Operations", "initial_sentiment": "positive"}
        ],
        "interactions": [
            {
                "interaction_id": "sum-int-1",
                "date": "2026-09-28",
                "type": "Discovery",
                "transcript": "Claire Vance loved the automated batch logging. Requested performance benchmarks."
            },
            {
                "interaction_id": "sum-int-2",
                "date": "2026-10-14",
                "type": "Demo Call",
                "transcript": "Alex demoed the workflow. Alex committed to send Claire the comparative benchmark latency figures by Oct 20. (OVERDUE COMMITMENT)."
            },
            {
                "interaction_id": "sum-int-3",
                "date": "2026-10-19",
                "type": "Check-in Attempt",
                "transcript": "Alex sent a quick note. No response from Claire Vance. Stakeholder silent for 18 days (since Oct 19). At risk."
            }
        ]
    },
    {
        "deal_id": "beacon-fintech",
        "company_name": "Beacon FinTech",
        "industry": "Financial Services",
        "deal_size": "$90,000",
        "status": "Open",
        "close_date": "2026-11-20",
        "competitor": "CloudFort",
        "key_stakeholders": [
            {"name": "Nadia Malik", "role": "VP Product", "initial_sentiment": "positive"},
            {"name": "Robert Chen", "role": "Procurement Director", "initial_sentiment": "neutral"}
        ],
        "interactions": [
            {
                "interaction_id": "bea-int-1",
                "date": "2026-10-05",
                "type": "Scoping",
                "transcript": "Nadia Malik stated initial budget was $120,000 for full enterprise roll-out."
            },
            {
                "interaction_id": "bea-int-2",
                "date": "2026-10-20",
                "type": "Budget Update Meeting",
                "transcript": "Robert Chen (Procurement Director) announced: 'Corporate reallocated our Q4 capital. Our budget has been updated and strictly capped at $90,000.' Contradiction/update from previous $120k figure."
            },
            {
                "interaction_id": "bea-int-3",
                "date": "2026-11-04",
                "type": "Proposal Adjustment",
                "transcript": "Alex revised enterprise scope to fit the updated $90k cap. Robert Chen confirmed security review is underway."
            }
        ]
    }
]

GROUND_TRUTH = {
    "dataset_summary": {
        "total_deals": 10,
        "closed_won": 4,
        "closed_lost": 2,
        "open": 4
    },
    "planted_patterns": [
        {
            "pattern_name": "CFO Pricing Objection Resolution (ROI Strategy)",
            "description": "When a CFO raises a pricing/budget objection, presenting an ROI case study/financial breakdown yields an 80%+ win rate (Acme Corp, Nexus Health, Vanguard Logistics won with ROI; Omni Finance lost when rep offered only a discount without ROI).",
            "evidence_deals": ["acme-corp", "nexus-health", "vanguard-logistics", "omni-finance"],
            "winning_action": "Share 3-year ROI financial model / case study within 48-72 hours of objection."
        },
        {
            "pattern_name": "Legal Review Stall Risk",
            "description": "Deals that stay in Legal Review for > 14 days without an active redline cycle have high probability of stalling or dying due to shifting corporate priorities (Titan Energy lost after 45 days in legal; Horizon Telecom currently at 18 days with overdue commitment).",
            "evidence_deals": ["titan-energy", "horizon-telecom"],
            "preventive_action": "Mandate maximum 48-hour SLA on redlines and proactively schedule alignment calls between general counsels."
        },
        {
            "pattern_name": "Silent Champion Risk",
            "description": "When the primary champion or economic buyer goes uncontacted or unresponsive for 14+ days, deal progression drops sharply (Summit BioTech champion silent for 18 days; Titan Energy champion went silent before cancellation).",
            "evidence_deals": ["summit-biotech", "titan-energy"],
            "preventive_action": "Trigger executive check-in or deliver overdue commitments immediately."
        }
    ]
}

def generate():
    deals_file = DATA_DIR / "deals.json"
    ground_truth_file = DATA_DIR / "ground_truth.json"

    with open(deals_file, "w", encoding="utf-8") as f:
        json.dump(DEALS, f, indent=2)
    print(f"Generated {len(DEALS)} synthetic deals at: {deals_file}")

    with open(ground_truth_file, "w", encoding="utf-8") as f:
        json.dump(GROUND_TRUTH, f, indent=2)
    print(f"Saved ground truth patterns at: {ground_truth_file}")

if __name__ == "__main__":
    generate()
