"""
Agent Orchestrator - Main API for all agent operations
Routes scenarios to the appropriate agent.
"""

import time
from .groq_client import GroqClient
from .linkup_wrapper import LinkupWrapper
from .email_agent import SmartEmailAgent


class AgentOrchestrator:
    def __init__(self):
        self.groq = GroqClient()
        self.linkup = LinkupWrapper()
        self.email_agent = SmartEmailAgent()

    def process(self, scenario: str, input_data: dict) -> dict:
        """
        Main entry point for all agent requests.

        Args:
            scenario: One of 'email', 'document', 'meeting'
            input_data: Dict with scenario-specific data

        Returns:
            {
                'reasoning_steps': [...],
                'linkup_sources': [...],
                'result': '...',
                'draft_reply': '...',
                'confidence': 0.95,
                'execution_time': 5.2
            }
        """
        start_time = time.time()

        try:
            if scenario == "email":
                result = self._process_email(input_data)
            elif scenario == "document":
                result = self._process_document(input_data)
            elif scenario == "meeting":
                result = self._process_meeting(input_data)
            else:
                raise ValueError(f"Unknown scenario: {scenario}")

            result['execution_time'] = round(time.time() - start_time, 2)
            return result

        except Exception as e:
            return {
                'error': str(e),
                'reasoning_steps': [f"Error occurred: {str(e)}"],
                'linkup_sources': [],
                'result': None,
                'execution_time': round(time.time() - start_time, 2)
            }

    def _process_email(self, input_data: dict) -> dict:
        """
        Process email scenario using SmartEmailAgent.

        Expected input_data: {
            'email_content': 'Email text...'
        }
        """
        email_content = input_data.get('email_content', '')
        result = self.email_agent.process(email_content)

        # Ensure draft_reply key exists for UI compatibility
        if 'draft_reply' not in result:
            result['draft_reply'] = result.get('result', '')

        return result

    def _process_document(self, input_data: dict) -> dict:
        """
        Process document scenario (stub - not yet implemented).

        Expected input_data: {
            'file_path': '/path/to/document.pdf',
            'question': 'Are payment terms standard?'
        }
        """
        return {
            'reasoning_steps': [
                "Extracting text from PDF...",
                "Identifying payment terms...",
                "Searching industry standards via Linkup...",
                "Comparing and analyzing..."
            ],
            'linkup_sources': [],
            'result': "Document analysis agent not yet implemented. Coming soon!",
            'confidence': 0.0
        }

    def _process_meeting(self, input_data: dict) -> dict:
        """
        Process meeting preparation scenario (stub - not yet implemented).

        Expected input_data: {
            'company_name': 'TechCorp',
            'meeting_context': 'Partnership discussion',
            'meeting_date': 'Tomorrow at 3pm'
        }
        """
        return {
            'reasoning_steps': [
                "Searching past interactions...",
                "Looking up recent company news via Linkup...",
                "Synthesizing briefing document..."
            ],
            'linkup_sources': [],
            'result': "Meeting preparation agent not yet implemented. Coming soon!",
            'confidence': 0.0
        }
