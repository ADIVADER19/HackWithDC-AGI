# Developer 2: Desktop UI (Streamlit)

## Your Responsibilities (8 hours)

### Hour 0-0.5: Setup
- [ ] Install Streamlit: `pip install streamlit`
- [ ] Test basic Streamlit app runs
- [ ] Familiarize with st.text_area, st.button, st.expander

### Hour 0.5-2: Main Layout
- [ ] Create `app.py` with sidebar navigation
- [ ] Add header/title
- [ ] Create scenario tabs (Email, Document, Meeting)
- [ ] Set up page config and styling

### Hour 2-3.5: Email Scenario UI
- [ ] Text area for email input
- [ ] "Analyze" button
- [ ] Display reasoning steps (st.expander)
- [ ] Show Linkup sources as cards
- [ ] Display draft reply
- [ ] Test with placeholder data

### Hour 3.5-5: Document Scenario UI
- [ ] File uploader for PDF
- [ ] Display extracted text preview
- [ ] Show analysis results in table
- [ ] Highlight flagged clauses
- [ ] Test with sample PDF

### Hour 5-6.5: Meeting Scenario UI
- [ ] Input for company name / meeting topic
- [ ] "Generate Briefing" button
- [ ] Display past interactions
- [ ] Show current news/research
- [ ] Formatted briefing output

### Hour 6.5-7.5: Reasoning Visualization
- [ ] Create reusable reasoning display component
- [ ] Progress bar for agent execution
- [ ] Expandable steps with details
- [ ] Linkup source cards with URLs
- [ ] Polish animations and transitions

### Hour 7.5-8: Polish & Testing
- [ ] Custom CSS for better styling
- [ ] Loading spinners
- [ ] Success/error messages
- [ ] Test all scenarios end-to-end

## Files You'll Create

```
src/ui/
├── __init__.py
├── app.py                  # Main Streamlit app
├── components/
│   ├── __init__.py
│   ├── email_ui.py         # Email scenario interface
│   ├── document_ui.py      # Document scenario interface
│   ├── meeting_ui.py       # Meeting scenario interface
│   └── reasoning_viz.py    # Reusable reasoning display
└── styles/
    └── custom.css          # Custom styling
```

## Integration Points

### Import from Agents (Developer 1):
```python
from src.agents.orchestrator import AgentOrchestrator

agent = AgentOrchestrator()
result = agent.process(scenario="email", input_data={"email_content": text})
```

### Import from Memory (Developer 3):
```python
from src.memory.store import MemoryStore

memory = MemoryStore()
memory.save_conversation(scenario, input_data, result)
```

## Key Components to Build

### app.py (Main Entry Point)
```python
import streamlit as st

st.set_page_config(
    page_title="AGI Desktop Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
scenario = st.sidebar.selectbox("Choose Scenario", 
    ["Email Intelligence", "Document Analysis", "Meeting Prep"])

# Route to appropriate component
if scenario == "Email Intelligence":
    from components.email_ui import render_email_ui
    render_email_ui()
```

### components/reasoning_viz.py
```python
def display_reasoning_steps(steps):
    """Display agent reasoning steps"""
    st.subheader("🧠 Reasoning Process")
    for i, step in enumerate(steps):
        with st.expander(f"Step {i+1}: {step[:50]}...", expanded=(i==0)):
            st.write(step)

def display_linkup_sources(sources):
    """Display Linkup search results as cards"""
    st.subheader("🔍 Web Research Sources")
    for source in sources:
        st.markdown(f"""
        **{source['title']}**  
        {source['snippet']}  
        [View Source]({source['url']})
        """)
```

## Streamlit Best Practices

1. **Use st.session_state** for preserving data between interactions
2. **st.spinner()** for loading states
3. **st.error() / st.success()** for feedback
4. **st.columns()** for layout
5. **Custom CSS** via st.markdown() for styling

## Testing Checklist

- [ ] All 3 scenarios have clean interfaces
- [ ] Reasoning steps display properly
- [ ] Linkup sources show with links
- [ ] Loading states work
- [ ] Errors handled gracefully
- [ ] UI is responsive and polished

## Tips

1. **Start simple** - Get basic layout working first
2. **Test with fake data** - Don't wait for backend
3. **Use st.write() for debugging** - See what data looks like
4. **Reload is your friend** - Streamlit auto-reloads on save
5. **Mobile-friendly** - Test at different widths

## Sample Code to Get Started

See `app.py` and `components/` for starter templates.
