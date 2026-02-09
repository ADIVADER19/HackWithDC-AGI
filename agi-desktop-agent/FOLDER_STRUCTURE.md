# Complete Project Folder Structure

```
agi-desktop-agent/
│
├── README.md                          # Main project documentation
├── FOLDER_STRUCTURE.md                # This file
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── config/                            # Configuration files
│   ├── .env.example                   # Example environment variables
│   └── .env                           # Your API keys (DO NOT COMMIT)
│
├── src/                               # Source code
│   │
│   ├── agents/                        # Developer 1: Backend Agents
│   │   ├── __init__.py
│   │   ├── README.md                  # Developer 1 guide
│   │   ├── orchestrator.py            # Main agent API (integration point)
│   │   ├── groq_client.py             # Groq/Llama 3.3 wrapper
│   │   ├── linkup_wrapper.py          # Linkup search integration
│   │   ├── email_agent.py             # TODO: Email intelligence agent
│   │   ├── document_agent.py          # TODO: Document analysis agent
│   │   └── meeting_agent.py           # TODO: Meeting prep agent
│   │
│   ├── ui/                            # Developer 2: Desktop Interface
│   │   ├── __init__.py
│   │   ├── README.md                  # Developer 2 guide
│   │   ├── app.py                     # Main Streamlit app (run this!)
│   │   ├── components/                # TODO: UI components
│   │   │   ├── __init__.py
│   │   │   ├── email_ui.py            # Email scenario UI
│   │   │   ├── document_ui.py         # Document scenario UI
│   │   │   ├── meeting_ui.py          # Meeting scenario UI
│   │   │   └── reasoning_viz.py       # Reasoning display component
│   │   └── styles/
│   │       └── custom.css             # TODO: Custom styling
│   │
│   ├── memory/                        # Developer 3: Memory System
│   │   ├── __init__.py
│   │   ├── README.md                  # TODO: Developer 3 guide
│   │   ├── store.py                   # TODO: JSON-based memory
│   │   └── search.py                  # TODO: Memory search functions
│   │
│   └── utils/                         # Shared utilities
│       ├── __init__.py
│       └── helpers.py                 # TODO: Common helper functions
│
├── tests/                             # Developer 3: Testing & Demo Data
│   ├── README.md                      # TODO: Testing guide
│   ├── demo_data/
│   │   ├── sample_emails.json         # TODO: Demo emails
│   │   ├── sample_contract.pdf        # TODO: Sample PDF
│   │   └── meeting_scenarios.json     # TODO: Meeting contexts
│   ├── test_agents.py                 # TODO: Agent tests
│   └── demo_script.md                 # TODO: Presentation script
│
├── docs/                              # Developer 4: Documentation
│   ├── README.md                      # TODO: Documentation guide
│   ├── architecture.md                # TODO: System architecture
│   ├── architecture_diagram.png       # TODO: Visual diagram
│   ├── presentation.pptx              # TODO: Demo presentation
│   └── evaluation_mapping.md          # TODO: How we meet criteria
│
└── data/                              # Local data storage (git-ignored)
    ├── conversations/
    │   ├── .gitkeep
    │   └── history.json               # Auto-generated
    ├── emails/
    │   ├── .gitkeep
    │   └── cache.json                 # Auto-generated
    └── documents/
        └── .gitkeep                   # Uploaded files stored here
```

## Key Integration Points

### Developer 1 → Developer 2 (Agents → UI)
```python
# In src/ui/app.py
from src.agents.orchestrator import AgentOrchestrator
agent = AgentOrchestrator()
result = agent.process(scenario="email", input_data={...})
```

### Developer 1 ← Developer 3 (Agents ← Memory)
```python
# In src/agents/*.py
from src.memory.store import MemoryStore
memory = MemoryStore()
past_data = memory.search(query="TechCorp")
```

### Developer 2 → Developer 3 (UI → Memory)
```python
# In src/ui/app.py
from src.memory.store import MemoryStore
memory = MemoryStore()
memory.save_conversation(scenario, input_data, result)
```

## Quick Navigation

- **Start here**: `README.md`
- **Run app**: `streamlit run src/ui/app.py`
- **Developer 1 guide**: `src/agents/README.md`
- **Developer 2 guide**: `src/ui/README.md`
- **Developer 3 guide**: `src/memory/README.md` (TODO)
- **Developer 4 guide**: `docs/README.md` (TODO)

## File Status Legend

- ✅ Created with starter code
- 📝 Template created, needs implementation
- ⏳ TODO: Needs to be created

### Current Status

**Developer 1 (Agents):**
- ✅ groq_client.py (starter template)
- ✅ linkup_wrapper.py (starter template)
- ✅ orchestrator.py (placeholder structure)
- ⏳ email_agent.py
- ⏳ document_agent.py
- ⏳ meeting_agent.py

**Developer 2 (UI):**
- ✅ app.py (functional placeholder)
- ⏳ components/email_ui.py
- ⏳ components/document_ui.py
- ⏳ components/meeting_ui.py
- ⏳ components/reasoning_viz.py

**Developer 3 (Memory):**
- ⏳ store.py
- ⏳ search.py
- ⏳ Demo data files

**Developer 4 (Docs):**
- ⏳ All documentation files

## Next Steps

1. Copy `config/.env.example` to `config/.env`
2. Add your API keys to `config/.env`
3. Run `pip install -r requirements.txt`
4. Test: `streamlit run src/ui/app.py`
5. Start building! Each developer has their own README with detailed tasks.
