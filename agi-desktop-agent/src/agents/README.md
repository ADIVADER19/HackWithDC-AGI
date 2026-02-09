# Developer 1: Backend Agents & Linkup Integration

## Your Responsibilities (8 hours)

### Hour 0-0.5: Setup
- [ ] Install dependencies: `pip install groq linkup-sdk pypdf2`
- [ ] Test Groq API connection
- [ ] Test Linkup API connection
- [ ] Verify both work with sample calls

### Hour 0.5-2: Linkup Integration
- [ ] Create `linkup_wrapper.py` with search function
- [ ] Implement query formulation logic
- [ ] Parse and format Linkup results
- [ ] Return sources with URLs and snippets

### Hour 2-3.5: Email Agent
- [ ] Create `email_agent.py`
- [ ] Entity extraction from email text
- [ ] Decide when to trigger Linkup search
- [ ] Draft reply incorporating research
- [ ] Test with sample email

### Hour 3.5-5: Document Agent
- [ ] Create `document_agent.py`
- [ ] PDF text extraction using PyPDF2
- [ ] Identify key clauses/terms
- [ ] Use Linkup to verify against standards
- [ ] Generate comparison report

### Hour 5-6.5: Meeting Agent
- [ ] Create `meeting_agent.py`
- [ ] Search memory for past context
- [ ] Use Linkup for current company news
- [ ] Synthesize briefing document

### Hour 6.5-7.5: Orchestrator
- [ ] Create `orchestrator.py`
- [ ] Unified interface routing to agents
- [ ] Handle agent responses
- [ ] Expose API for UI layer

### Hour 7.5-8: Testing
- [ ] Integration testing with UI
- [ ] Debug issues
- [ ] Optimize response times

## Files You'll Create

```
src/agents/
├── __init__.py
├── orchestrator.py       # Main API - routes to agents
├── email_agent.py        # Email intelligence
├── document_agent.py     # Document analysis
├── meeting_agent.py      # Meeting preparation
├── linkup_wrapper.py     # Linkup search integration
└── groq_client.py        # Groq/Llama 3.3 wrapper
```

## Integration Points

### Export to UI (Developer 2):
```python
from src.agents.orchestrator import AgentOrchestrator

agent = AgentOrchestrator()
result = agent.process(scenario="email", input_data=email_text)
```

### Import from Memory (Developer 3):
```python
from src.memory.store import MemoryStore

memory = MemoryStore()
history = memory.get_conversation_history()
```

## Key Functions to Implement

### orchestrator.py
```python
class AgentOrchestrator:
    def process(self, scenario: str, input_data: dict) -> dict:
        """
        Main entry point for all agent requests
        Returns: {
            'reasoning_steps': [...],
            'linkup_sources': [...],
            'result': '...',
            'confidence': 0.95
        }
        """
```

### linkup_wrapper.py
```python
def search_web(query: str) -> dict:
    """
    Search using Linkup API
    Returns: {
        'sources': [...],
        'snippets': [...],
        'urls': [...]
    }
    """
```

## Testing Checklist

- [ ] Email agent returns research + draft reply
- [ ] Document agent extracts and compares clauses
- [ ] Meeting agent synthesizes past + current info
- [ ] All responses include reasoning steps
- [ ] Linkup sources properly formatted
- [ ] Response time < 10 seconds per scenario

## Tips

1. **Test Groq first** - Make sure Llama 3.3 works before building agents
2. **Linkup is your differentiator** - Spend time making search intelligent
3. **Keep it simple** - No complex error handling, focus on happy path
4. **Use function calling** - Llama 3.3 has native tool support
5. **Cache Linkup results** - Don't re-search same queries

## Sample Code to Get Started

See `groq_client.py` and `linkup_wrapper.py` for starter templates.
