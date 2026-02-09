"""
Agent Orchestrator - Main API for all agent operations

Supports two modes:
  1. Direct: process(scenario="meeting", input_data={...})
  2. Routed: route(user_prompt) -> auto-classifies -> dispatches to agent(s)

With Google API integration (optional):
  - Fetches real emails from Gmail when enabled
  - Fetches real calendar events from Google Calendar when enabled
  - Falls back to local cache files if APIs unavailable
"""

import os
import time
from .groq_client import GroqClient
from .linkup_wrapper import LinkupWrapper
from .email_agent import SmartEmailAgent
from .document_agent import DocumentAgent
from .meeting_agent import MeetingAgent
from .router_agent import RouterAgent
from ..memory.store import MemoryStore
from ..memory.session_store import SessionStore


class AgentOrchestrator:
    def __init__(self):
        self.groq = GroqClient()
        self.linkup = LinkupWrapper()

        # Initialize Google API clients (optional)
        self.gmail_client = None
        self.calendar_client = None
        self._init_google_apis()

        # Initialize memory with optional Google clients
        self.memory = MemoryStore(
            gmail_client=self.gmail_client,
            calendar_client=self.calendar_client
        )

        # Initialize all agents
        self.email_agent = SmartEmailAgent()
        self.document_agent = DocumentAgent(self.groq, self.linkup)
        self.meeting_agent = MeetingAgent(self.groq, self.linkup, self.memory)
        self.router = RouterAgent(self.groq)
        self.sessions = SessionStore()

    def _init_google_apis(self):
        """
        Initialize Google API clients if ENABLE_GOOGLE_APIS is true.
        Gracefully handles missing credentials or network errors.
        """
        try:
            from dotenv import load_dotenv
            load_dotenv(os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'config', '.env'
            ))

            enable_google = os.getenv('ENABLE_GOOGLE_APIS', 'false').lower() == 'true'

            if not enable_google:
                print("[Orchestrator] Google APIs disabled (set ENABLE_GOOGLE_APIS=true to enable)")
                return

            # Import Google clients
            from ..integrations.google_auth import GoogleAuthHandler
            from ..integrations.gmail_client import GmailClient
            from ..integrations.calendar_client import CalendarClient

            # Initialize auth
            credentials_file = os.getenv(
                'GOOGLE_CREDENTIALS_FILE',
                os.path.join(
                    os.path.dirname(__file__),
                    '..', '..', 'config', 'google_credentials.json'
                )
            )

            if not os.path.exists(credentials_file):
                print(f"[Orchestrator] Google credentials not found at {credentials_file}")
                print("[Orchestrator] To enable Gmail/Calendar: download OAuth 2.0 credentials from Google Cloud Console")
                print("[Orchestrator] and save as config/google_credentials.json, then set ENABLE_GOOGLE_APIS=true")
                return

            auth = GoogleAuthHandler(credentials_file=credentials_file)
            self.gmail_client = GmailClient(auth)
            self.calendar_client = CalendarClient(auth)
            print("[Orchestrator] Google APIs initialized successfully")
            print("[Orchestrator] - Gmail client ready")
            print("[Orchestrator] - Google Calendar client ready")

        except ImportError as e:
            print(f"[Orchestrator] Google API libraries not installed: {e}")
            print("[Orchestrator] Install with: pip install google-auth-oauthlib")
        except Exception as e:
            print(f"[Orchestrator] Google API initialization failed: {e}")
            print("[Orchestrator] Falling back to local cache files")

    # -- Public API ---------------------------------------------------------

    def route(self, user_prompt: str) -> dict:
        """
        Auto-classify a free-form user prompt and dispatch to the
        correct agent(s).
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

        return envelope

    def route_and_save(self, user_prompt: str, session_id: str | None = None) -> dict:
        """
        Same as route(), but also persists the interaction to a session file.
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
        """Direct dispatch -- caller already knows the scenario."""
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

    # -- Private handlers ---------------------------------------------------

    def _process_email(self, input_data: dict) -> dict:
        """Process email scenario using SmartEmailAgent."""
        email_content = input_data.get('email_content', '')
        result = self.email_agent.process(email_content)

        # Ensure draft_reply key exists for UI compatibility
        if 'draft_reply' not in result:
            result['draft_reply'] = result.get('result', '')

        return result

    def _process_document(self, input_data: dict) -> dict:
        """Process document scenario using DocumentAgent."""
        file_path = input_data.get('file_path', '')
        question = input_data.get('question', '')
        return self.document_agent.process(file_path, question)

    def _process_meeting(self, input_data: dict) -> dict:
        """Process meeting scenario using MeetingAgent."""
        company_name = input_data.get('company_name', '')
        meeting_context = input_data.get('meeting_context', '')
        if not company_name:
            return self._error_result('No company name provided.')
        return self.meeting_agent.prepare_briefing(
            company_name=company_name,
            meeting_context=meeting_context
        )

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
