"""Main Email Agent - Orchestrates all components"""

import os
from datetime import datetime
from dotenv import load_dotenv

from sample_emails import get_sample_emails, print_email
from email_processor import EmailProcessor
from research_agent import ResearchAgent
from reply_generator import ReplyGenerator
from reasoning_tracker import ReasoningTracker

# Load environment variables
load_dotenv()

class EmailAgent:
    """Intelligent email agent that processes emails and generates responses"""
    
    def __init__(self):
        """Initialize all components"""
        self.processor = EmailProcessor()
        self.research_agent = ResearchAgent()
        self.reply_generator = ReplyGenerator()
        self.tracker = ReasoningTracker()
        
        self.processed_emails = []
        self.generated_replies = []
    
    def process_email(self, email: dict, perform_research: bool = True, generate_reply: bool = True) -> dict:
        """Process a single email completely"""
        
        print(f"\n{'🚀'*35}")
        print(f"📧 EMAIL AGENT PROCESSING EMAIL #{email['id']}")
        print(f"{'🚀'*35}\n")
        
        # Start tracking session
        self.tracker.start_session(
            email['id'],
            email['sender'],
            email['subject']
        )
        
        # Step 1: Extract entities
        print("1️⃣  ENTITY EXTRACTION")
        print(f"   Analyzing email structure and extracting key information...")
        extracted = self.processor.extract_entities(email)
        self.tracker.log_extraction(extracted)
        
        # Step 2: Research (optional)
        research = None
        if perform_research and extracted.get('research_queries'):
            print(f"\n2️⃣  WEB RESEARCH")
            print(f"   Searching for {len(extracted['research_queries'])} topics...")
            research = self.research_agent.research_topics(extracted['research_queries'])
            self.tracker.log_research(research)
        else:
            print(f"\n2️⃣  WEB RESEARCH - SKIPPED")
        
        # Step 3: Generate reply (optional)
        reply = None
        if generate_reply:
            print(f"\n3️⃣  REPLY GENERATION")
            print(f"   Drafting intelligent response...")
            reply = self.reply_generator.generate_reply(email, extracted, research)
            self.tracker.log_reply_generation(reply)
        else:
            print(f"\n3️⃣  REPLY GENERATION - SKIPPED")
        
        # Compile result
        result = {
            "email_id": email['id'],
            "email_from": email['sender'],
            "email_subject": email['subject'],
            "extracted_entities": extracted,
            "research_results": research,
            "generated_reply": reply,
            "reasoning_log": self.tracker.reasoning_log,
            "processed_at": datetime.now().isoformat()
        }
        
        # End tracking
        self.tracker.end_session(f"Processed email from {email['sender']}")
        
        # Store result
        self.processed_emails.append(result)
        if reply:
            self.generated_replies.append(reply)
        
        # Display results
        self._display_processing_results(email, extracted, research, reply)
        
        return result
    
    def process_batch(self, emails: list, perform_research: bool = True, generate_reply: bool = True) -> list:
        """Process multiple emails"""
        print(f"\n📬 BATCH PROCESSING {len(emails)} EMAILS\n")
        results = []
        
        for i, email in enumerate(emails, 1):
            print(f"\n[{i}/{len(emails)}] Processing email...")
            result = self.process_email(email, perform_research, generate_reply)
            results.append(result)
        
        return results
    
    def _display_processing_results(self, email: dict, extracted: dict, research: dict, reply: dict):
        """Display the processing results"""
        
        # Show original email
        print_email(email)
        
        # Show extracted entities
        print(self.processor.format_for_display(extracted))
        
        # Show research results
        if research:
            print(self.research_agent.summarize_research(research))
        
        # Show generated reply
        if reply:
            print(self.reply_generator.format_for_display(reply))
        
        # Show reasoning log
        print(self.tracker.format_log_display())
    
    def get_summary_report(self) -> str:
        """Generate a summary report of all processed emails"""
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"📊 EMAIL AGENT PROCESSING REPORT")
        report.append(f"{'='*70}\n")
        
        report.append(f"Total Emails Processed: {len(self.processed_emails)}")
        report.append(f"Replies Generated: {len(self.generated_replies)}")
        report.append(f"Processing Timestamp: {datetime.now().isoformat()}\n")
        
        report.append(f"{'─'*70}")
        report.append(f"PROCESSED EMAILS SUMMARY:")
        report.append(f"{'─'*70}\n")
        
        for result in self.processed_emails:
            report.append(f"📧 Email #{result['email_id']}")
            report.append(f"   From: {result['email_from']}")
            report.append(f"   Subject: {result['email_subject']}")
            
            extracted = result.get('extracted_entities', {})
            report.append(f"   • Key Topics: {len(extracted.get('key_topics', []))}")
            report.append(f"   • Action Items: {len(extracted.get('action_items', []))}")
            report.append(f"   • Research Queries: {len(extracted.get('research_queries', []))}")
            report.append(f"   • Urgency: {extracted.get('urgency_level', 'N/A')}")
            report.append("")
        
        report.append(f"{'='*70}\n")
        return "\n".join(report)
    
    def save_results(self, output_dir: str = None) -> str:
        """Save all processed emails and results"""
        if output_dir is None:
            output_dir = os.getenv('MEMORY_DIR', 'data/')
        
        import json
        from pathlib import Path
        
        output_path = Path(output_dir) / "email_agent_results"
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save processed emails
        results_file = output_path / f"processed_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.processed_emails, f, indent=2)
        
        print(f"✓ Results saved to: {results_file}")
        return str(results_file)

if __name__ == "__main__":
    print("🎯 EMAIL AGENT - Intelligent Email Processing System")
    print("=" * 70)
    
    # Initialize agent
    agent = EmailAgent()
    
    # Get sample emails
    emails = get_sample_emails()
    
    # Process first email as demo (no research to save time)
    print(f"\n📨 Demo: Processing first email with full features...\n")
    agent.process_email(emails[0], perform_research=False, generate_reply=True)
    
    # Show report
    print(agent.get_summary_report())
    
    # Save results
    agent.save_results()
