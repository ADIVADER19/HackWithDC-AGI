import streamlit as st
import time

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""
if "pending_task" not in st.session_state:
    st.session_state.pending_task = None
if "awaiting_review" not in st.session_state:
    st.session_state.awaiting_review = False

# ── CSS ──
st.markdown("""
<style>
header[data-testid="stHeader"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
div.block-container {
    padding-top: 0 !important; padding-bottom: 0 !important;
    padding-left: 0 !important; padding-right: 0 !important;
    max-width: 100% !important;
}
.stApp {
    background: #fbfbfd !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    margin: 0 !important; padding: 0 !important;
}
.stApp > div:first-child { margin: 0 !important; padding: 0 !important; }
div[data-testid="stAppViewContainer"] { padding: 0 !important; margin: 0 !important; }
section.main > div { padding-top: 0 !important; margin-top: 0 !important; }
.element-container:first-child { margin-top: 0 !important; padding-top: 0 !important; }

/* Text area */
div[data-testid="stTextArea"] textarea {
    background: #fff !important; border: 1px solid #e0e0e5 !important;
    border-radius: 0.75rem !important; padding: 0.85rem 1rem !important;
    font-size: 0.9375rem !important; color: #111827 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    resize: none !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* Suggestion card buttons */
.suggestion-card div.stButton > button {
    background: #fff !important; border: 1px solid #ebebef !important;
    border-radius: 0.75rem !important; padding: 1.5rem 1.25rem !important;
    height: auto !important;
    white-space: normal !important; color: #111827 !important;
    box-shadow: none !important; transition: box-shadow 0.15s ease !important;
    width: 100% !important;
}
.suggestion-card div.stButton > button:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
    border-color: #d0d0d8 !important; color: #111827 !important;
}

/* Secondary action buttons */
.action-button div.stButton > button {
    background: #fff !important; border: 1px solid #e0e0e5 !important;
    border-radius: 0.5rem !important; color: #374151 !important;
}
.action-button div.stButton > button:hover {
    background: #f3f4f6 !important; color: #111827 !important;
    border-color: #d0d0d8 !important;
}

/* Primary button */
div.stButton > button[kind="primary"] {
    background: #6366f1 !important; color: #fff !important;
    border: none !important; border-radius: 0.5rem !important;
    padding: 0.5rem 1.25rem !important; font-weight: 500 !important;
    font-size: 0.875rem !important; min-height: 2.5rem !important;
}
div.stButton > button[kind="primary"]:hover { background: #4f46e5 !important; }

/* All buttons baseline */
div.stButton > button {
    min-height: 2.5rem !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1.25rem !important;
}

/* Attach files expander */
div[data-testid="stExpander"] {
    border: 1px solid #e0e0e5 !important; border-radius: 0.5rem !important;
    background: #fff !important; margin-bottom: 0.5rem !important;
}
div[data-testid="stExpander"] summary {
    font-size: 0.8125rem !important; color: #6b7280 !important;
    font-weight: 500 !important; padding: 0.5rem 0.85rem !important;
}
div[data-testid="stExpander"] summary:hover { color: #111827 !important; }
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    padding: 0.5rem 0.85rem 0.75rem !important;
}

/* Timeline step cards */
.step-card {
    display: flex; align-items: flex-start; gap: 0.75rem;
    padding: 0.6rem 0.85rem; border-radius: 0.5rem;
    margin-bottom: 0.35rem; background: #fff;
    border: 1px solid #ebebef; font-size: 0.8125rem;
}
.step-card.active { border-color: #6366f1; background: #f5f3ff; }
.step-card.done { border-color: #d1fae5; background: #f0fdf4; }
.step-icon {
    width: 1.25rem; height: 1.25rem; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; flex-shrink: 0; margin-top: 0.1rem;
}
.step-icon.done { background: #10b981; color: #fff; }
.step-icon.active { background: #6366f1; color: #fff; }
.step-icon.pending { background: #e5e7eb; color: #9ca3af; }
.step-label { color: #111827; line-height: 1.4; }
.step-label.pending { color: #9ca3af; }

/* Chat bubbles */
.user-msg {
    background: #f5f3ff; border: 1px solid #e0e0e5; border-radius: 0.75rem;
    padding: 0.85rem 1.1rem; margin-bottom: 0.75rem;
}
.user-msg-label { font-size: 0.7rem; color: #6b7280; font-weight: 600; margin-bottom: 0.2rem; text-transform: uppercase; }
.user-msg-text { font-size: 0.9375rem; color: #111827; white-space: pre-wrap; }
.agent-msg {
    background: #fff; border: 1px solid #ebebef; border-radius: 0.75rem;
    padding: 0.85rem 1.1rem; margin-bottom: 0.75rem;
}
.agent-msg-label { font-size: 0.7rem; color: #6366f1; font-weight: 600; margin-bottom: 0.2rem; text-transform: uppercase; }
.agent-msg-text { font-size: 0.9375rem; color: #111827; white-space: pre-wrap; line-height: 1.6; }
.status-badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.75rem; font-weight: 500; padding: 0.25rem 0.6rem;
    border-radius: 1rem; margin-bottom: 0.75rem;
}
.status-approved { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.status-rejected { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.section-divider { border: none; border-top: 1px solid #ebebef; margin: 1.5rem 0; }
</style>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  1. HEADER (fixed top)
# ═══════════════════════════════════════════
is_processing = st.session_state.pending_task is not None
is_review = st.session_state.awaiting_review

if is_processing:
    status_label, dot_color = "Processing…", "#6366f1"
elif is_review:
    status_label, dot_color = "Awaiting review", "#f59e0b"
else:
    status_label, dot_color = "Ready", "#9ca3af"

st.markdown(f"""
<div style="position:fixed;top:0;left:0;right:0;z-index:9999;display:flex;align-items:center;justify-content:space-between;padding:0.75rem 1.5rem;background:#fff;border-bottom:1px solid #ebebef;">
  <div style="display:flex;align-items:center;gap:0.5rem;">
    <div style="width:1.75rem;height:1.75rem;border-radius:0.5rem;background:#6366f1;display:flex;align-items:center;justify-content:center;">
      <span class="material-symbols-outlined" style="font-size:15px;color:#fff;">shield</span>
    </div>
    <span style="font-weight:600;font-size:0.9375rem;color:#111827;">Assistant</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.4rem;font-size:0.8125rem;color:#6b7280;font-weight:500;">
    <span style="width:8px;height:8px;border-radius:9999px;background:{dot_color};display:inline-block;"></span>
    {status_label}
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="height:3.5rem;"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  2. HERO + SUGGESTION CARDS (always shown)
# ═══════════════════════════════════════════
st.markdown("""
<div style="display:flex;flex-direction:column;align-items:center;text-align:center;padding:3.5rem 1rem 2rem;">
  <div style="margin-bottom:1.25rem;color:#c4c7d0;">
    <span class="material-symbols-outlined" style="font-size:3.5rem;font-weight:200;">shield</span>
  </div>
  <div style="font-size:1.375rem;font-weight:600;color:#111827;margin-bottom:0.5rem;">Ready to assist</div>
  <div style="font-size:0.9375rem;color:#6b7280;max-width:28rem;line-height:1.6;">
    Describe a task in natural language and the assistant will help you complete it safely and transparently.
  </div>
</div>
""", unsafe_allow_html=True)

SUGGESTIONS = {
    "btn_doc": "Analyze the uploaded document — summarize key points and list important obligations.",
    "btn_cal": "Check my calendar for this week and find a free 30-minute slot for a team sync.",
    "btn_email": "Draft a professional follow-up email summarizing today's meeting and next steps.",
}
cols = st.columns([1, 1, 1, 1, 1])
with cols[1]:
    st.markdown('<div class="suggestion-card">', unsafe_allow_html=True)
    if st.button("📄\n\n**Document Analysis**\n\nUpload and analyze PDFs, contracts, reports — get structured summaries and key insights.", key="btn_doc", use_container_width=True):
        st.session_state.suggestion = SUGGESTIONS["btn_doc"]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with cols[2]:
    st.markdown('<div class="suggestion-card">', unsafe_allow_html=True)
    if st.button("📅\n\n**Calendar**\n\nView upcoming events, schedule meetings, and find optimal time slots automatically.", key="btn_cal", use_container_width=True):
        st.session_state.suggestion = SUGGESTIONS["btn_cal"]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with cols[3]:
    st.markdown('<div class="suggestion-card">', unsafe_allow_html=True)
    if st.button("✉️\n\n**Email**\n\nDraft, review, and send emails with context-aware suggestions and tone control.", key="btn_email", use_container_width=True):
        st.session_state.suggestion = SUGGESTIONS["btn_email"]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  3. CHAT HISTORY (between suggestions & input)
# ═══════════════════════════════════════════
has_messages = len(st.session_state.messages) > 0

if has_messages:
    _, chat_col, _ = st.columns([1, 2.5, 1])
    with chat_col:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if msg["type"] == "user":
                st.markdown(f"""
                <div class="user-msg">
                  <div class="user-msg-label">You</div>
                  <div class="user-msg-text">{msg["content"]}</div>
                </div>""", unsafe_allow_html=True)

            elif msg["type"] == "steps":
                st.markdown('<div style="margin-bottom:0.75rem;">', unsafe_allow_html=True)
                for step in msg["content"]:
                    st.markdown(f"""
                    <div class="step-card done">
                      <div class="step-icon done">✓</div>
                      <div class="step-label">{step}</div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            elif msg["type"] == "result":
                st.markdown(f"""
                <div class="agent-msg">
                  <div class="agent-msg-label">Assistant</div>
                  <div class="agent-msg-text">{msg["content"]}</div>
                </div>""", unsafe_allow_html=True)

            elif msg["type"] == "status":
                cls = "status-approved" if msg["content"] == "approved" else "status-rejected"
                icon = "✅" if msg["content"] == "approved" else "❌"
                label = "Approved" if msg["content"] == "approved" else "Rejected"
                st.markdown(f'<div class="status-badge {cls}">{icon} {label}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  4. PROCESSING ANIMATION (between chat & input)
# ═══════════════════════════════════════════
if st.session_state.pending_task is not None:
    _, proc_col, _ = st.columns([1, 2.5, 1])

    STEPS = [
        "Understanding your request…",
        "Researching relevant information…",
        "Analyzing data and context…",
        "Generating output…",
        "Preparing results for review",
    ]

    with proc_col:
        st.markdown("""
        <div style="font-size:0.8rem;font-weight:600;color:#6b7280;margin-bottom:0.5rem;text-transform:uppercase;">Agent Activity</div>
        """, unsafe_allow_html=True)

    timeline_placeholder = st.empty()

    for step_idx in range(len(STEPS)):
        steps_html = ""
        for i, label in enumerate(STEPS):
            if i < step_idx:
                cls, icon_cls, icon = "done", "done", "✓"
            elif i == step_idx:
                cls, icon_cls, icon = "active", "active", "●"
            else:
                cls, icon_cls, icon = "", "pending", "○"
            label_cls = "pending" if i > step_idx else ""
            steps_html += f"""
            <div class="step-card {cls}">
              <div class="step-icon {icon_cls}">{icon}</div>
              <div class="step-label {label_cls}">{label}</div>
            </div>"""

        with timeline_placeholder.container():
            _, c, _ = st.columns([1, 2.5, 1])
            with c:
                st.markdown(steps_html, unsafe_allow_html=True)
        time.sleep(1.2)

    st.session_state.messages.append({"type": "steps", "content": STEPS})

    result_text = (
        "Based on my analysis, here are the key findings:\n\n"
        "1. The document contains 3 main sections covering project scope, timeline, and budget.\n"
        "2. Key deadline: All deliverables due by March 15, 2026.\n"
        "3. Budget allocation: 40% development, 30% testing, 20% deployment, 10% contingency.\n"
        "4. Risk factors identified: resource availability, third-party dependencies.\n\n"
        "Recommended next steps:\n"
        "- Schedule a kickoff meeting with all stakeholders\n"
        "- Confirm resource allocation with team leads\n"
        "- Set up progress tracking milestones"
    )
    st.session_state.messages.append({"type": "result", "content": result_text})
    st.session_state.pending_task = None
    st.session_state.awaiting_review = True
    st.rerun()


# ═══════════════════════════════════════════
#  5. REVIEW BUTTONS (between chat & input)
# ═══════════════════════════════════════════
if st.session_state.awaiting_review:
    _, rev_col, _ = st.columns([1, 2.5, 1])
    with rev_col:
        st.markdown("""
        <div style="font-size:0.8125rem;color:#6b7280;margin-bottom:0.5rem;">Review the output above, then choose an action:</div>
        """, unsafe_allow_html=True)
        # Buttons temporarily disabled
        # b1, b2, b3, b4 = st.columns(4, gap="small")
        # with b2:
        #     st.markdown('<div class="action-button">', unsafe_allow_html=True)
        #     if st.button("✅ Approve", key="approve_btn", type="primary", use_container_width=True):
        #         st.session_state.messages.append({"type": "status", "content": "approved"})
        #         st.session_state.awaiting_review = False
        #         st.rerun()
        #     st.markdown('</div>', unsafe_allow_html=True)
        # with b3:
        #     st.markdown('<div class="action-button">', unsafe_allow_html=True)
        #     if st.button("✏️ Revise", key="revise_btn", use_container_width=True):
        #         st.session_state.pending_task = st.session_state.messages[-1]["content"] if st.session_state.messages else ""
        #         st.session_state.awaiting_review = False
        #         st.rerun()
        #     st.markdown('</div>', unsafe_allow_html=True)
        # with b4:
        #     st.markdown('<div class="action-button">', unsafe_allow_html=True)
        #     if st.button("❌ Reject", key="reject_btn", use_container_width=True):
        #         st.session_state.messages.append({"type": "status", "content": "rejected"})
        #         st.session_state.awaiting_review = False
        #         st.rerun()
        #     st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  6. INPUT BOX (always at the very end)
# ═══════════════════════════════════════════
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
_, input_col, _ = st.columns([1, 2, 1])
with input_col:
    user_input = st.text_area(
        "Task input",
        value=st.session_state.suggestion,
        placeholder="What would you like me to do?",
        key="task_input",
        height=110,
        label_visibility="collapsed",
    )
    with st.expander("📎 Attach files", expanded=False):
        uploaded_files = st.file_uploader(
            "Upload files",
            type=["pdf", "docx", "txt", "csv", "xlsx", "png", "jpg"],
            accept_multiple_files=True,
            key="file_upload",
            label_visibility="collapsed",
        )
    _, btn_col = st.columns([3.5, 1])
    with btn_col:
        run_clicked = st.button("Run ➜", key="run_btn", type="primary", use_container_width=True)

    if run_clicked and user_input.strip():
        st.session_state.messages.append({"type": "user", "content": user_input.strip()})
        st.session_state.pending_task = user_input.strip()
        st.session_state.suggestion = ""
        st.rerun()

st.markdown("""
<div style="text-align:center;margin-top:-0.25rem;margin-bottom:2rem;">
  <span style="font-size:0.75rem;color:#9ca3af;">or press Ctrl + Enter to submit</span>
</div>
""", unsafe_allow_html=True)
