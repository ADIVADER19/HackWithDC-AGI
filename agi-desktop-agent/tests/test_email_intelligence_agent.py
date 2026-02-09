#!/usr/bin/env python3
"""
Test script for Email Intelligence Agent
Demonstrates the complete workflow: analyze → research → draft
"""

import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def main():
    print("=" * 70)
    print("🧪 EMAIL INTELLIGENCE AGENT - COMPREHENSIVE TEST")
    print("=" * 70)

    try:
        # Import agent and demo emails
        from src.agents.email_intelligence_agent import EmailIntelligenceAgent
        from tests.demo_data.sample_emails import DEMO_EMAILS, list_demo_emails

        # Initialize agent
        print("\n🚀 Initializing Email Intelligence Agent...")
        agent = EmailIntelligenceAgent()
        print("✓ Agent initialized with Groq & Linkup\n")

        # List available emails
        print("📧 Available Demo Emails:")
        for key in list_demo_emails():
            email = DEMO_EMAILS[key]
            print(f"  • {key}: {email['metadata']['from']} - {email['subject']}")

        # Test with first email (Acme Ventures)
        test_key = "acme_ventures"
        test_email = DEMO_EMAILS[test_key]

        print(f"\n{'=' * 70}")
        print(f"📨 TESTING WITH: {test_key.upper()}")
        print(f"{'=' * 70}")
        print(
            f"From: {test_email['metadata']['from']} ({test_email['metadata']['company']})"
        )
        print(f"Subject: {test_email['subject']}")
        print(f"{'─' * 70}\n")

        # Analyze email
        print("🔄 Starting analysis workflow...\n")
        result = agent.analyze_email(
            email_content=test_email["content"], email_metadata=test_email["metadata"]
        )

        # Display reasoning steps
        print(f"\n{'=' * 70}")
        print("🧠 REASONING STEPS:")
        print(f"{'=' * 70}")
        for step in result["reasoning_steps"]:
            print(f"[{step['timestamp']}] {step['step']}")

        # Display entities found
        print(f"\n{'=' * 70}")
        print("🔍 ENTITIES EXTRACTED:")
        print(f"{'=' * 70}")
        if result["entities"]:
            for i, entity in enumerate(result["entities"], 1):
                print(f"{i}. {entity['name']} ({entity['type']})")
                print(f"   Context: {entity.get('context', 'N/A')}")
        else:
            print("No entities requiring research")

        # Display research findings
        print(f"\n{'=' * 70}")
        print("📚 RESEARCH FINDINGS:")
        print(f"{'=' * 70}")
        if result["research"]:
            for entity_name, research in result["research"].items():
                print(f"\n{entity_name}:")

                # Check if using existing knowledge
                if research.get("used_existing_knowledge"):
                    print(f"  ✓ Source: Existing Knowledge")
                    print(f"  Info: {research.get('known_info', 'N/A')[:100]}...")
                    print(f"  Reasoning: {research.get('reasoning', 'N/A')}")
                else:
                    sources = research.get("sources", [])
                    if sources:
                        print(f"  🔍 Source: Linkup Search ({len(sources)} results)")
                        for i, source in enumerate(sources[:3], 1):
                            print(f"    {i}. {source.get('title', 'No title')}")
                            print(f"       URL: {source.get('url', 'N/A')[:60]}...")
                    else:
                        print("  No sources found")
        else:
            print("No research conducted")

        # Display draft reply
        print(f"\n{'=' * 70}")
        print("✍️ DRAFTED REPLY:")
        print(f"{'=' * 70}")
        print(result["draft_reply"])

        # Display sources summary
        print(f"\n{'=' * 70}")
        print(f"📊 SUMMARY:")
        print(f"{'=' * 70}")
        print(f"Total Entities Found: {len(result['entities'])}")
        print(f"Total Sources Retrieved: {len(result['sources'])}")
        print(f"Execution Time: {result['execution_time']}s")
        print(f"Timestamp: {result['timestamp']}")

        # Display Smart Linkup Usage stats
        stats = result.get("stats", {})
        if stats:
            print(f"\n{'─' * 70}")
            print("🧠 SMART LINKUP USAGE METRICS:")
            print(f"{'─' * 70}")
            print(f"Total Entities Analyzed: {stats.get('total_entities', 0)}")
            print(
                f"Entities Searched (Linkup API): {stats.get('entities_searched', 0)}"
            )
            print(
                f"Entities Using Existing Knowledge: {stats.get('entities_known', 0)}"
            )
            print(f"Total Sources Retrieved: {stats.get('linkup_sources', 0)}")

            efficiency = stats.get("efficiency_pct", 0)
            print(f"Efficiency: {efficiency}% avoided unnecessary API calls")

            searches_avoided = stats.get("entities_known", 0)
            if searches_avoided > 0:
                estimated_savings = searches_avoided * 0.01
                print(
                    f"💰 Estimated Cost Saved: ${estimated_savings:.2f} (skipped {searches_avoided} API calls)"
                )

        print(f"\n{'=' * 70}")
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print(f"{'=' * 70}\n")

        return 0

    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("Make sure you're running from the project root:")
        print("  python tests/test_email_intelligence_agent.py")
        return 1
    except Exception as e:
        print(f"\n❌ Test Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
