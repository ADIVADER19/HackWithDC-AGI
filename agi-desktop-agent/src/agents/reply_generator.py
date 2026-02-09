"""Email reply generator using Groq AI and research data"""

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


class ReplyGenerator:
    """Generate intelligent email replies using Groq AI"""

    def __init__(self):
        """Initialize the reply generator with Groq client"""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))

    def generate_reply(
        self, email: dict, extracted: dict, research: dict = None
    ) -> dict:
        """Generate a reply based on email content and research"""

        # Prepare research context
        research_context = ""
        if research:
            research_context = self._format_research_context(research)

        prompt = f"""You are a professional email assistant. Generate a thoughtful, 
informative reply to the following email.

ORIGINAL EMAIL:
From: {email['sender']}
Subject: {email['subject']}
Priority: {email['priority']}
Body:
{email['body']}

EXTRACTED INFORMATION:
- Key Topics: {', '.join(extracted.get('key_topics', []))}
- Action Items: {', '.join(extracted.get('action_items', []))}
- Questions to Address: {', '.join(extracted.get('decision_needed', []))}

{f'''RESEARCH FINDINGS:
{research_context}''' if research_context else ''}

INSTRUCTIONS:
1. Address all action items and questions mentioned
2. Be professional and informative
3. If research was provided, reference relevant findings
4. Be concise but thorough (2-3 paragraphs)
5. Include specific recommendations where appropriate
6. Maintain a positive and collaborative tone

Generate a professional email reply (include greeting and closing):"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            reply_text = response.choices[0].message.content.strip()

            return {
                "status": "success",
                "reply": reply_text,
                "original_email_id": email.get("id"),
                "original_from": email["sender"],
                "original_subject": email["subject"],
                "generated_at": datetime.now().isoformat(),
                "used_research": research is not None,
            }

        except Exception as e:
            print(f"❌ Error generating reply: {e}")
            return {
                "status": "error",
                "error": str(e),
                "original_email_id": email.get("id"),
                "original_from": email["sender"],
            }

    def generate_batch_replies(
        self, emails: list, extracted_list: list, research_list: list = None
    ) -> list:
        """Generate replies for multiple emails"""
        replies = []

        for i, email in enumerate(emails):
            print(f"\n✍️  Generating reply {i+1}/{len(emails)}...")
            research = research_list[i] if research_list else None
            reply = self.generate_reply(email, extracted_list[i], research)
            replies.append(reply)

        return replies

    def _format_research_context(self, research: dict) -> str:
        """Format research data for use in prompt"""
        context = []

        if "results" in research:
            for query, result in research["results"].items():
                if "error" not in result:
                    context.append(f"\n📌 Topic: {query}")
                    for i, item in enumerate(result.get("results", [])[:3], 1):
                        url = item.get("url", "N/A")
                        title = item.get("title", "N/A")
                        context.append(f"   {i}. {title} ({url})")

        return "\n".join(context)

    def format_for_display(self, reply_result: dict) -> str:
        """Format reply for display"""
        output = []
        output.append(f"\n{'='*70}")
        output.append(f"📬 REPLY TO: {reply_result.get('original_from')}")
        output.append(f"RE: {reply_result.get('original_subject')}")
        output.append(f"{'='*70}\n")

        if reply_result.get("status") == "error":
            output.append(f"❌ ERROR: {reply_result.get('error')}")
        else:
            output.append(reply_result.get("reply", "No reply generated"))
            if reply_result.get("used_research"):
                output.append("\n[✓ This reply was informed by research data]")

        output.append(f"\n{'='*70}")
        return "\n".join(output)


if __name__ == "__main__":
    from email_processor import EmailProcessor
    from research_agent import ResearchAgent
    from sample_emails import get_sample_emails

    print("🚀 Reply Generator - AI Email Response Demo\n")

    # Get sample email
    email = get_sample_emails()[0]

    # Extract entities
    processor = EmailProcessor()
    print(f"📧 Processing: {email['subject']}\n")
    extracted = processor.extract_entities(email)

    # Research topics
    if "research_queries" in extracted:
        agent = ResearchAgent()
        print(f"📚 Researching {len(extracted['research_queries'])} topics...\n")
        research = agent.research_topics(extracted["research_queries"])
    else:
        research = None

    # Generate reply
    generator = ReplyGenerator()
    print(f"✍️  Generating reply...\n")
    reply = generator.generate_reply(email, extracted, research)

    # Display
    print(generator.format_for_display(reply))
