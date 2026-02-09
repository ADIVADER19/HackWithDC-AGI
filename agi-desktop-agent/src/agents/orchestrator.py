"""
Agent Orchestrator - Main API for all agent operations

Supports two modes:
  1. Direct: process(scenario="meeting", input_data={...})
  2. Routed: route(user_prompt) → auto-classifies → dispatches to agent(s)
"""

import time
from .groq_client import GroqClient
from .linkup_wrapper import LinkupWrapper
from .meeting_agent import MeetingAgent
from .router_agent import RouterAgent
from ..memory.store import MemoryStore
from ..memory.session_store import SessionStore


class AgentOrchestrator:
    def __init__(self):
        self.groq = GroqClient()
        self.linkup = LinkupWrapper()
        self.memory = MemoryStore()
        self.router = RouterAgent(self.groq)
        self.meeting_agent = MeetingAgent(self.groq, self.linkup, self.memory)
        self.sessions = SessionStore()

    # ── Public API ─────────────────────────────────────────────

    def route(self, user_prompt: str) -> dict:
        """
        Auto-classify a free-form user prompt and dispatch to the
        correct agent(s).  Returns a unified envelope:

        {
            'route': { ... },            # Router classification
            'results': {                  # One key per scenario that ran
                'meeting': { ... },
                'email': { ... },
            },
            'primary_scenario': 'meeting',
            'execution_time': 4.2
        }
        """
        start = time.time()

        classification = self.router.classify(user_prompt)
        scenarios = classification.get('scenarios', [])
        params = classification.get('params', {})

        results = {}
        for scenario in scenarios:
            scenario_params = params.get(scenario, {})
            try:
                results[scenario] = self.process(scenario, scenario_params)
            except Exception as e:
                results[scenario] = self._error_result(str(e))

        envelope = {
            'route': classification,
            'results': results,
            'primary_scenario': classification.get('primary_scenario', scenarios[0] if scenarios else 'meeting'),
            'execution_time': round(time.time() - start, 2)
        }

        # Auto-persist to session if session_id provided or create new
        # (caller can pass session_id in a future chatbot integration)
        return envelope

    def route_and_save(self, user_prompt: str, session_id: str | None = None) -> dict:
        """
        Same as route(), but also persists the interaction to a session file.
        Returns the envelope with 'session_id' added.
        """
        if session_id is None:
            session_id = self.sessions.create_session()

        envelope = self.route(user_prompt)
        self.sessions.append(
            session_id=session_id,
            user_query=user_prompt,
            route=envelope.get('route', {}),
            results=envelope.get('results', {}),
            execution_time=envelope.get('execution_time', 0),
        )
        envelope['session_id'] = session_id
        return envelope

    def process(self, scenario: str, input_data: dict) -> dict:
        """Direct dispatch — caller already knows the scenario."""
        start = time.time()
        try:
            if scenario == "email":
                result = self._process_email(input_data)
            elif scenario == "document":
                result = self._process_document(input_data)
            elif scenario == "meeting":
                result = self._process_meeting(input_data)
            else:
                raise ValueError(f"Unknown scenario: {scenario}")
            result['execution_time'] = round(time.time() - start, 2)
            return result
        except Exception as e:
            r = self._error_result(str(e))
            r['execution_time'] = round(time.time() - start, 2)
            return r

    # ── Private handlers ───────────────────────────────────────

    def _process_meeting(self, input_data: dict) -> dict:
        company_name = input_data.get('company_name', '')
        meeting_context = input_data.get('meeting_context', '')
        if not company_name:
            return self._error_result('No company name provided.')
        return self.meeting_agent.prepare_briefing(
            company_name=company_name,
            meeting_context=meeting_context
        )

    def _process_email(self, input_data: dict) -> dict:
        """Placeholder — will be replaced by teammate's EmailAgent."""
        return {
            'scenario': 'email',
            'reasoning_steps': [
                {'step': 1, 'action': 'Analyze email content', 'detail': 'Parsing sender, subject, body...', 'status': 'complete'},
                {'step': 2, 'action': 'Entity detection', 'detail': f"Detected company: {input_data.get('company_name', 'N/A')}", 'status': 'complete'},
                {'step': 3, 'action': 'Web research', 'detail': 'Searching Linkup for context...', 'status': 'complete'},
                {'step': 4, 'action': 'Draft reply', 'detail': 'Generating response with Llama 3.3...', 'status': 'complete'},
            ],
            'linkup_sources': [],
            'result': '[Email agent not yet integrated — placeholder response]',
            'result_data': {
                'analysis': 'Email analysis will appear here once the Email Agent is integrated.',
                'draft_reply': 'Dear [Name],\n\nThank you for your email...',
                'sentiment': 'Neutral',
            },
            'confidence': 0.0,
            'source_attribution': {'memory_pct': 0, 'linkup_pct': 0, 'llm_pct': 100,
                                   'linkup_sources_count': 0, 'verification_status': 'N/A'},
        }

    def _process_document(self, input_data: dict) -> dict:
        """Placeholder — will be replaced by Document Agent."""
        return {
            'scenario': 'document',
            'reasoning_steps': [
                {'step': 1, 'action': 'Extract text from PDF', 'detail': 'Reading uploaded document...', 'status': 'complete'},
                {'step': 2, 'action': 'Identify clauses', 'detail': 'Scanning for key contract sections...', 'status': 'complete'},
                {'step': 3, 'action': 'Industry comparison', 'detail': 'Searching Linkup for standards...', 'status': 'complete'},
                {'step': 4, 'action': 'Generate report', 'detail': 'Compiling findings...', 'status': 'complete'},
            ],
            'linkup_sources': [],
            'result': '[Document agent not yet integrated — placeholder]',
            'result_data': {
                'clauses_found': [],
                'risk_flags': [],
                'summary': 'Document analysis will appear here once the Document Agent is integrated.',
            },
            'confidence': 0.0,
            'source_attribution': {'memory_pct': 0, 'linkup_pct': 0, 'llm_pct': 100,
                                   'linkup_sources_count': 0, 'verification_status': 'N/A'},
        }

    @staticmethod
    def _error_result(message: str) -> dict:
        return {
            'reasoning_steps': [{'step': 1, 'action': 'Error', 'detail': message, 'status': 'error'}],
            'linkup_sources': [],
            'result': f"Error: {message}",
            'briefing_data': {},
            'confidence': 0.0,
            'execution_time': 0,
            'source_attribution': {
                'memory_pct': 0, 'linkup_pct': 0, 'llm_pct': 100,
                'memory_interactions': 0, 'linkup_sources_count': 0,
                'data_freshness': 'N/A', 'sections': {},
                'verification_status': 'Unverified'
            },
        }


if __name__ == "__main__":
    o = AgentOrchestrator()
    r = o.route("Prepare me for a meeting with TechCorp about AI partnership")
    print(r['route'])
    print(f"Time: {r['execution_time']}s")
