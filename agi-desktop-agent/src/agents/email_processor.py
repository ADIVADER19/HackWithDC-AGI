"""Email processor with entity extraction using Groq AI"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to ensure config is loaded
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from groq import Groq

# Load environment variables from config directory
env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)


class EmailProcessor:
    """Process emails and extract key entities and requirements"""

    def __init__(self):
        """Initialize the email processor with Groq client"""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))

    def extract_entities(self, email: dict) -> dict:
        """Extract entities from email using Groq"""

        prompt = f"""Analyze this email and extract the following information in JSON format:

EMAIL:
From: {email['sender']}
Subject: {email['subject']}
Date: {email['date']}
Priority: {email['priority']}
Body: {email['body']}

Please extract and return ONLY valid JSON (no markdown, no extra text) with these keys:
{{
    "key_topics": [list of main topics discussed],
    "action_items": [specific requests or tasks mentioned],
    "research_queries": [web search queries that would help answer the email],
    "decision_needed": [any decisions the sender is asking for],
    "entities": {{
        "companies": [mentioned companies],
        "technologies": [mentioned technologies/tools],
        "metrics": [mentioned metrics, budgets, timelines]
    }},
    "sentiment": "positive|neutral|negative",
    "urgency_level": "low|medium|high",
    "summary": "one sentence summary of the email"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Parse the response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            extracted = json.loads(content.strip())

            # Add metadata
            extracted["email_id"] = email.get("id")
            extracted["sender"] = email["sender"]
            extracted["subject"] = email["subject"]
            extracted["processed_at"] = datetime.now().isoformat()

            return extracted

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response content: {content}")
            return {
                "email_id": email.get("id"),
                "sender": email["sender"],
                "subject": email["subject"],
                "error": str(e),
                "raw_response": content,
            }
        except Exception as e:
            print(f"❌ Error extracting entities: {e}")
            return {
                "email_id": email.get("id"),
                "sender": email["sender"],
                "error": str(e),
            }

    def process_batch(self, emails: list) -> list:
        """Process multiple emails"""
        results = []
        for email in emails:
            print(f"\n📧 Processing email from {email['sender']}...")
            extracted = self.extract_entities(email)
            results.append(extracted)
            print(
                f"   ✓ Extracted {len(extracted.get('action_items', []))} action items"
            )
        return results

    def format_for_display(self, extracted: dict) -> str:
        """Format extracted data for display"""
        output = []
        output.append(f"\n{'='*70}")
        output.append(f"📧 EMAIL ID: {extracted.get('email_id')}")
        output.append(f"FROM: {extracted.get('sender')}")
        output.append(f"SUBJECT: {extracted.get('subject')}")
        output.append(f"{'='*70}")

        if "error" in extracted:
            output.append(f"❌ ERROR: {extracted['error']}")
            return "\n".join(output)

        output.append(f"\n📌 SUMMARY:")
        output.append(f"   {extracted.get('summary', 'N/A')}")

        output.append(f"\n🎯 KEY TOPICS:")
        for topic in extracted.get("key_topics", []):
            output.append(f"   • {topic}")

        output.append(f"\n✅ ACTION ITEMS:")
        for item in extracted.get("action_items", []):
            output.append(f"   □ {item}")

        output.append(f"\n🔍 RESEARCH QUERIES:")
        for query in extracted.get("research_queries", []):
            output.append(f"   • {query}")

        if extracted.get("entities", {}).get("companies"):
            output.append(f"\n🏢 COMPANIES MENTIONED:")
            for company in extracted["entities"]["companies"]:
                output.append(f"   • {company}")

        if extracted.get("entities", {}).get("technologies"):
            output.append(f"\n💻 TECHNOLOGIES MENTIONED:")
            for tech in extracted["entities"]["technologies"]:
                output.append(f"   • {tech}")

        if extracted.get("entities", {}).get("metrics"):
            output.append(f"\n📊 KEY METRICS:")
            for metric in extracted["entities"]["metrics"]:
                output.append(f"   • {metric}")

        output.append(f"\n📍 URGENCY: {extracted.get('urgency_level', 'N/A').upper()}")
        output.append(f"😊 SENTIMENT: {extracted.get('sentiment', 'N/A').upper()}")
        output.append(f"\n{'='*70}")

        return "\n".join(output)


if __name__ == "__main__":
    from sample_emails import get_sample_emails

    print("🚀 Email Processor - Entity Extraction Demo\n")

    processor = EmailProcessor()
    emails = get_sample_emails()

    # Process first email as demo
    email = emails[0]
    print(f"Processing: {email['subject']}")
    print(f"From: {email['sender']}\n")

    extracted = processor.extract_entities(email)
    print(processor.format_for_display(extracted))
