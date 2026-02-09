"""
Smart Email Intelligence Agent (Copilot version)
- Entity extraction, prioritization, research, and reply drafting
- Returns: reasoning_steps, linkup_sources, result (draft reply), confidence
"""

from .email_intelligence_agent import EmailIntelligenceAgent


class SmartEmailAgent:
    def __init__(self, recipient_company="DataFlow AI"):
        self.agent = EmailIntelligenceAgent(recipient_company=recipient_company)

    def process(self, email_content, email_metadata=None):
        """
        Main entry point for the UI/orchestrator.
        Args:
            email_content: str, the email body
            email_metadata: dict, optional metadata
        Returns:
            dict with keys: reasoning_steps, linkup_sources, result, confidence
        """
        result = self.agent.analyze_email(email_content, email_metadata)
        # Compose output for UI/orchestrator
        return {
            "reasoning_steps": result.get("reasoning_steps", []),
            "linkup_sources": result.get("sources", []),
            "result": result.get("draft_reply", ""),
            "confidence": result.get("stats", {})
            .get("validation", {})
            .get("credibility_score", 0.7),
        }


# Example usage for orchestrator:
# from src.agents.email_agent import SmartEmailAgent
# agent = SmartEmailAgent()
# output = agent.process(email_content)
