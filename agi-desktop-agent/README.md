# AGI-Inspired Desktop Intelligence Agent

8-Hour Sprint Project - 4 Developer Tracks

## Quick Start

### 1. Setup Environment (First 20 minutes)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy example config
cp config/.env.example config/.env

# Edit config/.env and add your API keys:
# - GROQ_API_KEY (get from groq.com)
# - LINKUP_API_KEY (get from linkup.so)
```

### 3. Run the Application
```bash
streamlit run src/ui/app.py
```

## Project Structure

```
agi-desktop-agent/
├── src/
│   ├── agents/          # Developer 1: Backend agents + Linkup
│   ├── ui/              # Developer 2: Streamlit desktop interface
│   ├── memory/          # Developer 3: Memory system + testing
│   └── utils/           # Shared utilities
├── docs/                # Developer 4: Architecture + documentation
├── tests/               # Test scenarios and demo data
├── config/              # Configuration files
└── data/                # Local data storage (JSON files)
```

## Developer Tracks

### Developer 1: Backend Agents (src/agents/)
- Groq + Llama 3.3 integration
- Linkup search wrapper
- Email, Document, Meeting agents
- Agent orchestrator

### Developer 2: Desktop UI (src/ui/)
- Streamlit interface
- Scenario navigation
- Reasoning visualization
- Results display

### Developer 3: Memory & Testing (src/memory/ + tests/)
- JSON-based memory system
- Demo data creation
- End-to-end testing
- Demo script preparation

### Developer 4: Docs & Architecture (docs/)
- System architecture diagram
- API documentation
- Presentation materials
- Evaluation criteria mapping

## Integration Points

All tracks communicate through:
- `src/agents/orchestrator.py` - Central agent API
- `src/memory/store.py` - Shared memory interface
- Environment variables in `config/.env`

## 8-Hour Timeline

- Hour 0: Setup + sync (30 mins)
- Hour 2: First integration check
- **Hour 4: Email scenario must work end-to-end** ⚠️
- Hour 6: All scenarios functional
- Hour 7.5: Final rehearsal + backup recording

Good luck! 🚀
