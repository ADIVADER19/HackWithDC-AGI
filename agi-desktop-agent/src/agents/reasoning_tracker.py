"""Reasoning tracker for logging agent decision-making process"""

import json
import os
from datetime import datetime
from pathlib import Path


class ReasoningTracker:
    """Track and log agent reasoning steps"""

    def __init__(self, log_dir: str = None):
        """Initialize the reasoning tracker"""
        if log_dir is None:
            log_dir = os.getenv("MEMORY_DIR", "data/")

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.reasoning_log = []
        self.current_session_id = None

    def start_session(self, email_id: int, sender: str, subject: str) -> str:
        """Start a new reasoning session"""
        self.current_session_id = f"email_{email_id}_{datetime.now().timestamp()}"

        self.log_step(
            "SESSION_START",
            {
                "email_id": email_id,
                "sender": sender,
                "subject": subject,
                "timestamp": datetime.now().isoformat(),
            },
        )

        return self.current_session_id

    def log_step(self, step_name: str, details: dict):
        """Log a reasoning step"""
        step = {
            "step_name": step_name,
            "session_id": self.current_session_id,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }

        self.reasoning_log.append(step)
        print(f"   📝 [{step_name}] {details}")

    def log_extraction(self, extracted_data: dict):
        """Log entity extraction step"""
        self.log_step(
            "ENTITY_EXTRACTION",
            {
                "key_topics": len(extracted_data.get("key_topics", [])),
                "action_items": len(extracted_data.get("action_items", [])),
                "research_queries": len(extracted_data.get("research_queries", [])),
                "sentiment": extracted_data.get("sentiment"),
                "urgency": extracted_data.get("urgency_level"),
            },
        )

    def log_research(self, research_data: dict):
        """Log research step"""
        total_results = 0
        queries_searched = 0

        if "results" in research_data:
            queries_searched = len(research_data["results"])
            for result in research_data["results"].values():
                if "results" in result:
                    total_results += len(result.get("results", []))

        self.log_step(
            "WEB_RESEARCH",
            {
                "queries_searched": queries_searched,
                "total_results_found": total_results,
                "depth": research_data.get("depth", "standard"),
            },
        )

    def log_reply_generation(self, reply_data: dict):
        """Log reply generation step"""
        status = reply_data.get("status", "unknown")
        self.log_step(
            "REPLY_GENERATION",
            {
                "status": status,
                "used_research": reply_data.get("used_research", False),
                "reply_length": (
                    len(reply_data.get("reply", "")) if status == "success" else 0
                ),
            },
        )

    def log_decision(
        self, decision_name: str, reasoning: str, options: list, choice: str
    ):
        """Log a decision made by the agent"""
        self.log_step(
            "DECISION",
            {
                "decision": decision_name,
                "reasoning": reasoning,
                "options": options,
                "chosen": choice,
            },
        )

    def end_session(self, summary: str = None):
        """End the current session"""
        self.log_step(
            "SESSION_END",
            {
                "timestamp": datetime.now().isoformat(),
                "total_steps": len(self.reasoning_log),
                "summary": summary,
            },
        )

    def save_session(self, email_id: int = None) -> str:
        """Save the reasoning log to file"""
        if not self.reasoning_log:
            print("⚠️  No reasoning log to save")
            return None

        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"reasoning_log_{email_id}_{timestamp}.json"
            if email_id
            else f"reasoning_log_{timestamp}.json"
        )
        filepath = self.log_dir / filename

        # Save to file
        with open(filepath, "w") as f:
            json.dump(self.reasoning_log, f, indent=2)

        print(f"✓ Reasoning log saved: {filepath}")
        return str(filepath)

    def get_session_summary(self) -> dict:
        """Get a summary of the current session"""
        summary = {
            "session_id": self.current_session_id,
            "total_steps": len(self.reasoning_log),
            "timestamp_start": None,
            "timestamp_end": None,
            "steps_by_type": {},
        }

        if self.reasoning_log:
            summary["timestamp_start"] = self.reasoning_log[0].get("timestamp")
            summary["timestamp_end"] = self.reasoning_log[-1].get("timestamp")

            # Count steps by type
            for step in self.reasoning_log:
                step_name = step.get("step_name")
                summary["steps_by_type"][step_name] = (
                    summary["steps_by_type"].get(step_name, 0) + 1
                )

        return summary

    def format_log_display(self) -> str:
        """Format the reasoning log for display"""
        output = []
        output.append(f"\n{'='*70}")
        output.append(f"🧠 AGENT REASONING LOG")
        output.append(f"{'='*70}")

        for i, step in enumerate(self.reasoning_log, 1):
            output.append(f"\n[{i}] {step['step_name']}")
            output.append(f"    Time: {step['timestamp']}")

            details = step.get("details", {})
            for key, value in details.items():
                output.append(f"    • {key}: {value}")

        summary = self.get_session_summary()
        output.append(f"\n{'='*70}")
        output.append(f"SUMMARY:")
        output.append(f"  Total Steps: {summary['total_steps']}")

        for step_type, count in summary.get("steps_by_type", {}).items():
            output.append(f"  {step_type}: {count}")

        output.append(f"{'='*70}")
        return "\n".join(output)


if __name__ == "__main__":
    print("🚀 Reasoning Tracker - Decision Logging Demo\n")

    tracker = ReasoningTracker()

    # Simulate a reasoning session
    tracker.start_session(1, "john.smith@techcorp.com", "Project Alpha Budget Review")

    tracker.log_step(
        "EMAIL_RECEIVED",
        {"priority": "high", "length": 450, "contains_questions": True},
    )

    tracker.log_extraction(
        {
            "key_topics": ["Budget", "Timeline", "Competition"],
            "action_items": ["Research market trends", "Confirm team size"],
            "research_queries": ["AI market trends 2026"],
            "sentiment": "neutral",
            "urgency_level": "high",
        }
    )

    tracker.log_research(
        {
            "results": {
                "AI market trends": {
                    "results": [{"title": "Result 1"}, {"title": "Result 2"}]
                }
            }
        }
    )

    tracker.log_decision(
        "BUDGET_RECOMMENDATION",
        "Based on competitive analysis and market trends",
        ["Maintain $500k", "Increase to $650k", "Request $750k"],
        "Increase to $650k",
    )

    tracker.log_reply_generation(
        {
            "status": "success",
            "used_research": True,
            "reply": "Here is the recommended response...",
        }
    )

    tracker.end_session("Successfully processed email and generated response")

    # Display and save
    print(tracker.format_log_display())
    tracker.save_session(1)
