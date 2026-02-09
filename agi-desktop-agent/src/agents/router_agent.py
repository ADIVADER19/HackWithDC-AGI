"""
Router Agent — Meta-agent that classifies user intent and routes to the right scenario agent(s).

Uses Groq (Llama 3.3 70B) to determine:
  1. Which scenario(s) the user's prompt maps to (meeting, email, document)
  2. Extracted parameters for each scenario
  3. Whether multiple agents need to run in parallel
"""

import json
import re


class RouterAgent:
    """
    Lightweight Groq-based classifier that routes user prompts
    to the correct scenario agent(s).
    """

    ROUTER_SYSTEM_PROMPT = """You are a request classifier for a desktop intelligence agent.
Given a user's natural language request, classify which agent(s) should handle it.

Available agents:
- "meeting": Meeting preparation — briefings, talking points, company research before meetings
- "email": Email intelligence — analyzing emails, drafting replies, email research
- "document": Document analysis — contract review, clause extraction, PDF analysis

Rules:
1. A request can trigger ONE or MULTIPLE agents.
2. Extract relevant parameters for each triggered agent.
3. If the intent is ambiguous, pick the most likely single agent.
4. If the user mentions both a meeting AND an email, trigger both.

Return ONLY valid JSON (no markdown, no explanation):
{
  "scenarios": ["meeting"],
  "primary_scenario": "meeting",
  "params": {
    "meeting": {"company_name": "TechCorp", "meeting_context": "partnership discussion"},
    "email": {"email_content": "", "company_name": ""},
    "document": {"question": "", "file_hint": ""}
  },
  "summary": "Prepare a meeting briefing for TechCorp about partnership"
}

Only include scenario keys in "params" for scenarios listed in "scenarios".
For meeting: extract company_name (REQUIRED) and meeting_context.
For email: extract email_content or company_name if mentioned.
For document: extract the analysis question.
"""

    def __init__(self, groq_client):
        self.groq = groq_client

    def classify(self, user_prompt: str) -> dict:
        """
        Classify user intent and extract parameters.

        Returns:
            {
                'scenarios': ['meeting'],
                'primary_scenario': 'meeting',
                'params': { 'meeting': { 'company_name': '...', ... } },
                'summary': '...'
            }
        """
        try:
            response = self.groq.chat(
                messages=[
                    {"role": "system", "content": self.ROUTER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )

            content = response.get('content', '{}')
            cleaned = content.strip()

            # Strip markdown code fences if present
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                lines = [l for l in lines if not l.strip().startswith('```')]
                cleaned = '\n'.join(lines)

            result = json.loads(cleaned)

            # Validate required fields
            if 'scenarios' not in result or not result['scenarios']:
                result['scenarios'] = [self._fallback_classify(user_prompt)]
                result['primary_scenario'] = result['scenarios'][0]

            if 'primary_scenario' not in result:
                result['primary_scenario'] = result['scenarios'][0]

            if 'params' not in result:
                result['params'] = {}

            # Heuristic fallback if company_name missing for meeting
            if 'meeting' in result.get('scenarios', []):
                meeting_params = result['params'].get('meeting', {})
                company_name = (meeting_params.get('company_name') or '').strip()
                if not company_name:
                    extracted = self._extract_company_name(user_prompt)
                    if extracted:
                        meeting_params['company_name'] = extracted
                        meeting_params.setdefault('meeting_context', user_prompt)
                        result['params']['meeting'] = meeting_params

            return result

        except Exception as e:
            # Fallback: keyword-based classification
            scenario = self._fallback_classify(user_prompt)
            return {
                'scenarios': [scenario],
                'primary_scenario': scenario,
                'params': self._fallback_params(scenario, user_prompt),
                'summary': user_prompt,
                'router_error': str(e)
            }

    def _fallback_classify(self, prompt: str) -> str:
        """Simple keyword-based fallback if Groq classification fails."""
        prompt_lower = prompt.lower()

        meeting_keywords = ['meeting', 'briefing', 'prepare me', 'talking points',
                            'meet with', 'meeting with', 'call with', 'presentation']
        email_keywords = ['email', 'reply', 'draft', 'respond', 'inbox',
                          'mail', 'message from', 'write back']
        document_keywords = ['document', 'contract', 'pdf', 'clause', 'analyze file',
                             'upload', 'extract', 'review document']

        scores = {
            'meeting': sum(1 for k in meeting_keywords if k in prompt_lower),
            'email': sum(1 for k in email_keywords if k in prompt_lower),
            'document': sum(1 for k in document_keywords if k in prompt_lower),
        }

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else 'meeting'

    def _fallback_params(self, scenario: str, prompt: str) -> dict:
        """Generate minimal params when Groq parsing fails."""
        if scenario == 'meeting':
            return {
                'meeting': {
                    'company_name': self._extract_company_name(prompt),
                    'meeting_context': prompt
                }
            }
        elif scenario == 'email':
            return {'email': {'email_content': prompt, 'company_name': ''}}
        elif scenario == 'document':
            return {'document': {'question': prompt, 'file_hint': ''}}
        return {}

    def _extract_company_name(self, prompt: str) -> str:
        """Best-effort entity extraction for company name."""
        text = (prompt or "").strip()
        if not text:
            return ""

        patterns = [
            r'\bmeeting with\s+([^.,;:\n]+)',
            r'\bmeet with\s+([^.,;:\n]+)',
            r'\bwith\s+([^.,;:\n]+)',
            r'\bfor\s+([^.,;:\n]+)',
        ]
        stop_words = {
            'tomorrow', 'today', 'at', 'about', 'regarding', 'on', 'to', 'and',
            'use', 'prepare', 'briefing', 'talking', 'points', 'next', 'steps',
            'context', 'with', 'from'
        }

        for pat in patterns:
            match = re.search(pat, text, flags=re.IGNORECASE)
            if match:
                chunk = match.group(1).strip().strip('"\'')
                tokens = chunk.split()
                filtered = []
                for token in tokens:
                    if token.lower() in stop_words:
                        break
                    filtered.append(token)
                candidate = " ".join(filtered) if filtered else chunk
                candidate = candidate.strip().strip('"\'')
                if candidate:
                    return " ".join(candidate.split()[:4])

        # Fallback: CamelCase or ALLCAPS token
        camel = re.search(r'\b[A-Z][a-z]+[A-Z][A-Za-z]*\b', text)
        if camel:
            return camel.group(0)
        caps = re.findall(r'\b[A-Z]{2,}\b', text)
        return caps[0] if caps else ""
