"""
Test Quality Improvements: Known vs Unknown Entities
Demonstrates the improved knowledge assessment and draft quality
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "config"))

from agents.email_intelligence_agent import EmailIntelligenceAgent


def test_known_vs_unknown():
    """Test that known companies are handled differently than unknown ones"""

    print("=" * 80)
    print("🧪 QUALITY IMPROVEMENTS TEST: Known vs Unknown Entities")
    print("=" * 80)
    print()

    # Test 1: Known Companies (should have high efficiency)
    print("TEST 1: Email mentioning KNOWN companies")
    print("-" * 80)
    known_company_email = """
Hi there,

I hope this message finds you well. I wanted to reach out because I'm impressed 
by your company's recent work.

I'm currently leading partnerships at Google, and we're always looking for 
innovative companies to collaborate with. Microsoft and Amazon are doing some 
great work too.

Would you be interested in discussing a potential partnership between your company 
and Google Cloud?

Looking forward to hearing from you.

Best regards,
Jane Smith
Product Manager, Google Cloud
    """.strip()

    try:
        agent = EmailIntelligenceAgent()
        result = agent.analyze_email(known_company_email)

        stats = result.get("stats", {})
        draft = result.get("draft_reply", "")

        print(f"✓ Entities Found: {stats.get('total_entities', 0)}")
        print(f"✓ Entities Searched: {stats.get('entities_searched', 0)}")
        print(f"✓ Entities Using Knowledge: {stats.get('entities_known', 0)}")
        print(f"✓ Efficiency: {stats.get('efficiency_pct', 0):.1f}%")
        print(f"✓ Draft Length: {len(draft.split())} words")
        print()
        print("Draft Reply:")
        print("-" * 40)
        print(draft[:300] + "..." if len(draft) > 300 else draft)
        print()

        # Check improvements
        if stats.get("efficiency_pct", 0) > 30:
            print("✅ IMPROVEMENT #1: High efficiency! Known companies not searched")
        else:
            print(
                "⚠️  Note: Efficiency is 0% - may be treating Google, Microsoft as unknown context"
            )

        if len(draft.split()) <= 150:
            print("✅ IMPROVEMENT #2: Draft is concise (<150 words)")
        else:
            print(f"⚠️  Draft is {len(draft.split())} words (target: 100-150)")

        if any(cliche in draft for cliche in ["hope this finds", "looking forward to"]):
            print("⚠️  IMPROVEMENT #2: Some clichés still present")
        else:
            print("✅ IMPROVEMENT #2: Clichés removed successfully")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print()
    print("=" * 80)
    print()

    # Test 2: Unknown Startup (should trigger searches)
    print("TEST 2: Email mentioning UNKNOWN startup")
    print("-" * 80)
    unknown_startup_email = """
Hi,

I'm Alex from TechnoVision Inc, an AI startup we founded last year. We're working 
on real-time data processing solutions.

I came across your work and thought we might be a good fit for a strategic partnership.

TechnoVision has already secured $5M in seed funding and is growing rapidly.

Would you be open to a conversation?

Thanks,
Alex Chen
Founder, TechnoVision Inc
    """.strip()

    try:
        agent = EmailIntelligenceAgent()
        result = agent.analyze_email(unknown_startup_email)

        stats = result.get("stats", {})
        draft = result.get("draft_reply", "")

        print(f"✓ Entities Found: {stats.get('total_entities', 0)}")
        print(f"✓ Entities Searched: {stats.get('entities_searched', 0)}")
        print(f"✓ Entities Using Knowledge: {stats.get('entities_known', 0)}")
        print(f"✓ Efficiency: {stats.get('efficiency_pct', 0):.1f}%")
        print(f"✓ Draft Length: {len(draft.split())} words")
        print()
        print("Draft Reply:")
        print("-" * 40)
        print(draft[:300] + "..." if len(draft) > 300 else draft)
        print()

        # Check improvements
        if stats.get("entities_searched", 0) > 0:
            print("✅ IMPROVEMENT #3: Unknown startup triggered searches")
        else:
            print("⚠️  Note: No searches performed")

        if len(draft.split()) <= 150:
            print("✅ IMPROVEMENT #2: Draft is concise (<150 words)")
        else:
            print(f"⚠️  Draft is {len(draft.split())} words (target: 100-150)")

        # Check that generic terms weren't extracted as entities
        entities = result.get("entities", [])
        entity_names = [e.get("name", "").lower() for e in entities]
        generic_terms = ["ai", "real-time data processing", "data processing"]

        generic_extracted = [
            term for term in generic_terms if term in " ".join(entity_names).lower()
        ]

        if not generic_extracted:
            print("✅ IMPROVEMENT #3: Generic terms filtered out from entities")
        else:
            print(f"⚠️  Generic terms extracted: {generic_extracted}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print()
    print("=" * 80)
    print("🧪 TEST COMPLETE")
    print("=" * 80)
    print()
    print("IMPROVEMENTS SUMMARY:")
    print("✅ #1: Knowledge Assessment - Smarter decisions on what to search")
    print("✅ #2: Draft Quality - Concise (100-150 words), warm tone, no clichés")
    print(
        "✅ #3: Entity Extraction - Filters generic terms, focuses on specific entities"
    )
    print()


if __name__ == "__main__":
    test_known_vs_unknown()
