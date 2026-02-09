"""
AGI Desktop Intelligence Agent - Unified Chat UI
Single chat interface with auto-routing to scenario agents.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="AGI Desktop Intelligence Agent",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS: reasoning timeline + source bars + layout ─────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem; font-weight: 700; color: #1a73e8;
        text-align: center; margin-bottom: 0.3rem;
    }
    .sub-header {
        text-align: center; color: #666; font-size: 0.92rem;
        margin-bottom: 1.2rem;
    }
    .source-card {
        background: #f0f4ff; padding: 0.8rem 1rem;
        border-radius: 6px; margin: 0.4rem 0; font-size: 0.9rem;
    }

    /* ── Reasoning Timeline ─────────────────────────────────── */
    .timeline { padding: 0; margin: 0.4rem 0; }
    .timeline-step {
        position: relative; padding: 0 0 0 28px; margin-bottom: 0;
    }
    .timeline-step:not(:last-child)::before {
        content: ''; position: absolute; left: 8px; top: 20px;
        bottom: -2px; width: 2px; background: #d0d7de;
    }
    .timeline-step::after {
        content: ''; position: absolute; left: 3px; top: 6px;
        width: 12px; height: 12px; border-radius: 50%;
        background: #1a73e8; border: 2px solid #fff;
        box-shadow: 0 0 0 2px #1a73e8;
    }
    .timeline-step.error::after {
        background: #d93025; box-shadow: 0 0 0 2px #d93025;
    }
    .timeline-step.pending::after {
        background: #f9ab00; box-shadow: 0 0 0 2px #f9ab00;
    }
    .timeline-heading {
        font-weight: 600; font-size: 0.9rem; color: #1a1a1a; line-height: 1.5;
    }
    .timeline-detail {
        font-size: 0.8rem; color: #666; margin: 1px 0 8px 0; line-height: 1.35;
    }

    /* ── Source bars ────────────────────────────────────────── */
    .source-bar-wrap { margin: 0.35rem 0; }
    .source-bar-label { font-size: 0.82rem; color: #444; margin-bottom: 2px; }
    .source-bar-track {
        background: #e8e8e8; border-radius: 4px; height: 8px;
        width: 100%; overflow: hidden;
    }
    .source-bar-fill {
        height: 100%; border-radius: 4px; transition: width 0.4s ease;
    }
    .source-bar-fill.linkup  { background: #1a73e8; }
    .source-bar-fill.memory  { background: #34a853; }
    .source-bar-fill.llm     { background: #f9ab00; }

    /* ── Briefing sections ─────────────────────────────────── */
    .briefing-section {
        background: #fafbfc; border: 1px solid #e1e4e8;
        border-radius: 8px; padding: 1rem 1.2rem; margin-bottom: 0.7rem;
    }
    .briefing-section h4 { margin: 0 0 0.4rem 0; color: #1a73e8; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# Rendering helpers (defined first so they're callable below)
# ══════════════════════════════════════════════════════════════

def _source_bar(label, pct, css_class):
    st.markdown(f"""
    <div class="source-bar-wrap">
        <div class="source-bar-label">{label}: <strong>{pct}%</strong></div>
        <div class="source-bar-track">
            <div class="source-bar-fill {css_class}" style="width:{pct}%"></div>
        </div>
    </div>""", unsafe_allow_html=True)


def _render_timeline(steps):
    html = ['<div class="timeline">']
    for step in steps:
        if isinstance(step, dict):
            cls = ' error' if step.get('status') == 'error' else (' pending' if step.get('status') == 'pending' else '')
            html.append(f'<div class="timeline-step{cls}">'
                        f'<div class="timeline-heading">{step.get("action", "Processing")}</div>'
                        f'<div class="timeline-detail">{step.get("detail", "")}</div></div>')
        else:
            html.append(f'<div class="timeline-step"><div class="timeline-heading">{step}</div></div>')
    html.append('</div>')
    st.markdown('\n'.join(html), unsafe_allow_html=True)


def _render_meeting_result(result):
    past = result.get('past_interactions', {})
    briefing = result.get('briefing_data', {})
    sources = result.get('linkup_sources', [])

    if briefing:
        st.markdown(f'<div class="briefing-section"><h4>Company Overview</h4>{briefing.get("company_overview", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="briefing-section"><h4>Relationship Context</h4>{briefing.get("past_context", "No past interactions found.")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="briefing-section"><h4>Recent News</h4>{briefing.get("recent_news", "No recent news available.")}</div>', unsafe_allow_html=True)
        points = briefing.get('talking_points', [])
        if points:
            pts = ''.join(f"<li>{p}</li>" for p in points)
            st.markdown(f'<div class="briefing-section"><h4>Talking Points</h4><ol>{pts}</ol></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="briefing-section"><h4>Risks and Notes</h4>{briefing.get("risks_and_notes", "None identified.")}</div>', unsafe_allow_html=True)
    else:
        st.text(result.get('result', 'No briefing generated.'))

    with st.expander("Past Interactions", expanded=False):
        if past.get('emails'):
            for em in past['emails'][:5]:
                body = (em.get('body', '') or '')[:250]
                st.markdown(f'<div class="source-card"><strong>{em.get("subject","")}</strong><br>'
                            f'From: {em.get("from","")} | Date: {em.get("date","")}<br><em>{body}</em></div>', unsafe_allow_html=True)
        else:
            st.caption("No past emails found.")
        real = [c for c in past.get('conversations', []) if not c.get('briefing_generated')]
        if real:
            for conv in real[:5]:
                notes = (conv.get('notes', '') or '')[:250]
                st.markdown(f'<div class="source-card"><strong>{conv.get("topic","")}</strong><br>'
                            f'Date: {conv.get("date","")} | Outcome: {conv.get("outcome","N/A")}<br><em>{notes}</em></div>', unsafe_allow_html=True)
        else:
            st.caption("No past meetings found.")

    with st.expander("Web Sources", expanded=False):
        if sources:
            for src in sources:
                st.markdown(f'<div class="source-card"><strong>{src.get("title","Untitled")}</strong><br>'
                            f'{src.get("snippet","")}<br>'
                            f'<a href="{src.get("url","#")}" target="_blank">View</a></div>', unsafe_allow_html=True)
        else:
            st.caption("No web sources.")


def _render_email_result(result):
    data = result.get('result_data', {})
    st.markdown(f'<div class="briefing-section"><h4>Email Analysis</h4>{data.get("analysis", result.get("result", ""))}</div>', unsafe_allow_html=True)
    if data.get('sentiment'):
        st.markdown(f'<div class="briefing-section"><h4>Sentiment</h4>{data["sentiment"]}</div>', unsafe_allow_html=True)
    if data.get('draft_reply'):
        st.markdown(f'<div class="briefing-section"><h4>Draft Reply</h4><pre>{data["draft_reply"]}</pre></div>', unsafe_allow_html=True)


def _render_document_result(result):
    data = result.get('result_data', {})
    st.markdown(f'<div class="briefing-section"><h4>Document Summary</h4>{data.get("summary", result.get("result", ""))}</div>', unsafe_allow_html=True)
    flags = data.get('risk_flags', [])
    if flags:
        fl = ''.join(f"<li>{f}</li>" for f in flags)
        st.markdown(f'<div class="briefing-section"><h4>Risk Flags</h4><ul>{fl}</ul></div>', unsafe_allow_html=True)


def _render_scenario(scenario, result, total_time):
    attribution = result.get('source_attribution', {})
    steps = result.get('reasoning_steps', [])

    col_main, col_side = st.columns([3, 1])

    with col_side:
        st.markdown("#### Source Breakdown")
        _source_bar("Web Research", attribution.get('linkup_pct', 0), "linkup")
        _source_bar("Local Memory", attribution.get('memory_pct', 0), "memory")
        _source_bar("LLM Knowledge", attribution.get('llm_pct', 100), "llm")
        st.markdown(f"<span style='font-size:0.82rem;color:#888;'>Confidence: "
                    f"<b>{result.get('confidence', 0):.0%}</b> &nbsp; "
                    f"Time: <b>{result.get('execution_time', total_time)}s</b></span>",
                    unsafe_allow_html=True)

    with col_main:
        with st.expander("Reasoning", expanded=False):
            _render_timeline(steps)

        if scenario == "meeting":
            _render_meeting_result(result)
        elif scenario == "email":
            _render_email_result(result)
        elif scenario == "document":
            _render_document_result(result)
        else:
            st.write(result.get('result', 'No output.'))

        st.download_button(
            label="Download as Text",
            data=result.get('result', ''),
            file_name=f"{scenario}_result.txt",
            mime="text/plain",
        )


# ══════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### AGI Desktop Agent")
    st.caption("Powered by Llama 3.3 70B + Linkup")
    st.markdown("---")
    st.markdown("**How to use**")
    st.markdown("""Type any request in the chat box. The agent
automatically detects what you need:

- *Meeting prep* -- \"Prepare me for a meeting with TechCorp\"
- *Email analysis* -- \"Analyze this email from Acme Corp\"
- *Document review* -- \"Review this contract's payment terms\"

You can combine requests too.""")

    st.markdown("---")
    st.markdown("**Status**")
    st.success("Groq API Connected")
    st.success("Linkup API Connected")

    # ── Session History ────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Past Sessions**")
    from src.memory.session_store import SessionStore as _SS
    _sidebar_store = _SS()
    _past_sessions = _sidebar_store.list_sessions(limit=15)
    if _past_sessions:
        for _s in _past_sessions:
            _label = _s['title'][:45] + ('...' if len(_s['title']) > 45 else '')
            _count = _s['interaction_count']
            if st.button(f"{_label}  ({_count})", key=f"sess_{_s['session_id']}", use_container_width=True):
                _full = _sidebar_store.get_session(_s['session_id'])
                if _full and _full['interactions']:
                    last = _full['interactions'][-1]
                    st.session_state['envelope'] = {
                        'route': last.get('route', {}),
                        'results': last.get('results', {}),
                        'primary_scenario': last.get('route', {}).get('primary_scenario', 'meeting'),
                        'execution_time': last.get('execution_time', 0),
                        'session_id': _s['session_id'],
                    }
                    st.session_state['user_query'] = last.get('user_query', '')
                    st.session_state['active_session_id'] = _s['session_id']
                    st.rerun()
    else:
        st.caption("No sessions yet. Run a query to start one.")

    if st.button("New Session", use_container_width=True):
        for k in ['envelope', 'user_query', 'active_session_id']:
            st.session_state.pop(k, None)
        st.rerun()


# ══════════════════════════════════════════════════════════════
# Main content
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="main-header">AGI Desktop Intelligence Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask anything -- the agent auto-routes to the right tool.</div>', unsafe_allow_html=True)

# ── Chat input ─────────────────────────────────────────────────
with st.form("chat_form", clear_on_submit=False):
    user_query = st.text_area(
        "prompt", height=90,
        placeholder="e.g., Prepare me for a meeting with TechCorp about AI partnership",
        label_visibility="collapsed",
    )
    run_btn = st.form_submit_button("Run", type="primary")


# ── Processing ─────────────────────────────────────────────────
if run_btn and user_query:
    from src.agents.orchestrator import AgentOrchestrator
    agent = AgentOrchestrator()

    # Reuse existing session or create new
    session_id = st.session_state.get('active_session_id', None)

    with st.status("Thinking...", expanded=True) as status_box:
        st.write("Classifying your request...")
        envelope = agent.route_and_save(user_query, session_id=session_id)
        route_info = envelope['route']
        scenarios = route_info.get('scenarios', [])

        st.write(f"Detected: **{', '.join(s.title() for s in scenarios)}**")
        if route_info.get('summary'):
            st.write(f"_{route_info['summary']}_")
        status_box.update(label="Done", state="complete", expanded=False)

    st.session_state['envelope'] = envelope
    st.session_state['user_query'] = user_query
    st.session_state['active_session_id'] = envelope.get('session_id')

elif run_btn and not user_query:
    st.warning("Please type a request first.")


# ── Render results ─────────────────────────────────────────────
if 'envelope' in st.session_state:
    envelope = st.session_state['envelope']
    results = envelope.get('results', {})
    total_time = envelope.get('execution_time', 0)
    scenario_keys = list(results.keys())

    if len(scenario_keys) > 1:
        tabs = st.tabs([s.title() for s in scenario_keys])
        for i, key in enumerate(scenario_keys):
            with tabs[i]:
                _render_scenario(key, results[key], total_time)
    elif scenario_keys:
        _render_scenario(scenario_keys[0], results[scenario_keys[0]], total_time)


# ── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.caption("Built with Streamlit | Powered by Llama 3.3 70B + Linkup")
