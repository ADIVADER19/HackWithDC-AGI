"""
AGI Desktop Intelligence Agent - Complete Streamlit App
All 3 Scenarios: Email Intelligence, Document Analysis, Meeting Preparation
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Page configuration
st.set_page_config(
    page_title="AGI Desktop Intelligence Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    /* Main styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1a73e8 0%, #34a853 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .scenario-description {
        text-align: center;
        color: #5f6368;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Cards */
    .reasoning-step {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        font-weight: 500;
    }
    
    .source-card {
        background-color: #e8f0fe;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1a73e8;
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    
    .source-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .result-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        padding: 2rem;
        border-radius: 0.75rem;
        border: 2px solid #34a853;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(52, 168, 83, 0.15);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 1rem;
        line-height: 1.8;
        color: #202124;
    }
    
    .warning-card {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #fbbc04;
        margin: 1rem 0;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .status-info {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
    }
    
    /* Progress indicator */
    .progress-text {
        font-size: 0.9rem;
        color: #5f6368;
        font-style: italic;
        margin: 0.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "current_result" not in st.session_state:
    st.session_state.current_result = None

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 AGI Desktop Agent")
    st.markdown("*Powered by Llama 3.3 + Linkup*")
    st.markdown("---")

    scenario = st.radio(
        "**Select Scenario:**",
        [
            "🎯 Overview",
            "📧 Email Intelligence",
            "📄 Document Analysis",
            "📅 Meeting Preparation",
        ],
        index=0,
    )

    st.markdown("---")

    # Connection status
    st.markdown("### 🔌 System Status")

    try:
        from src.agents.groq_client import GroqClient

        groq = GroqClient()
        if groq.test_connection():
            st.success("✅ Groq API Connected")
        else:
            st.error("❌ Groq API Failed")
    except Exception as e:
        st.warning("⚠️ Groq API Not Configured")

    try:
        from src.agents.linkup_wrapper import LinkupWrapper

        linkup = LinkupWrapper()
        if linkup.test_connection():
            st.success("✅ Linkup API Connected")
        else:
            st.error("❌ Linkup API Failed")
    except Exception as e:
        st.warning("⚠️ Linkup API Not Configured")

    st.markdown("---")
    st.markdown("### 📊 Evaluation Criteria")
    st.caption("✓ Generality (3 domains)")
    st.caption("✓ Autonomy (ReAct loop)")
    st.caption("✓ Reasoning Quality")
    st.caption("✓ Context Awareness")
    st.caption("✓ Information Synthesis")
    st.caption("✓ Privacy & Security")
    st.caption("✓ Usability")


# Helper function to display reasoning steps
def display_reasoning_steps(steps):
    st.markdown("### 🧠 Agent Reasoning Process")
    for i, step in enumerate(steps, 1):
        st.markdown(
            f'<div class="reasoning-step">Step {i}: {step}</div>',
            unsafe_allow_html=True,
        )


# Helper function to display Linkup sources
def display_linkup_sources(sources):
    st.markdown("### 🔍 Web Research Results")
    st.caption(f"Found {len(sources)} relevant sources via Linkup")

    if not sources:
        st.info("No external research was needed for this query.")
        return

    for i, source in enumerate(sources, 1):
        st.markdown(
            f"""
        <div class="source-card">
            <strong>📌 Source {i}: {source.get('title', 'Unknown Title')}</strong><br/>
            <p style="margin: 0.5rem 0; color: #5f6368;">{source.get('snippet', 'No description available')}</p>
            <a href="{source.get('url', '#')}" target="_blank" style="color: #1a73e8; text-decoration: none;">
                🔗 View Full Source →
            </a>
        </div>
        """,
            unsafe_allow_html=True,
        )


# Main content
st.markdown(
    '<div class="main-header">🤖 AGI Desktop Intelligence Agent</div>',
    unsafe_allow_html=True,
)

# ==================== OVERVIEW SCREEN ====================
if scenario == "🎯 Overview":
    st.markdown(
        '<p class="scenario-description">Choose a scenario to experience AI-powered intelligence with real-time web research</p>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        ### 📧 Email Intelligence
        **What it does:**
        - Analyzes incoming emails
        - Researches unknown entities with Linkup
        - Drafts intelligent responses
        
        **Use case:** 
        Reply to investor inquiry with context about their portfolio
        
        **Demonstrates:**
        Autonomy • Information Synthesis • Reasoning
        """
        )

    with col2:
        st.markdown(
            """
        ### 📄 Document Analysis
        **What it does:**
        - Extracts text from PDFs
        - Identifies key clauses
        - Verifies against industry standards
        
        **Use case:**
        Review SaaS contract payment terms
        
        **Demonstrates:**
        Generality • Multi-Domain • Practical Value
        """
        )

    with col3:
        st.markdown(
            """
        ### 📅 Meeting Preparation
        **What it does:**
        - Searches past interactions
        - Researches current company news
        - Generates comprehensive briefings
        
        **Use case:**
        Prepare for partnership meeting
        
        **Demonstrates:**
        Context Awareness • Memory Integration
        """
        )

    st.info("👈 Select a scenario from the sidebar to get started")

# ==================== SCENARIO 1: EMAIL INTELLIGENCE ====================
elif scenario == "📧 Email Intelligence":
    st.markdown("## 📧 Email Intelligence Agent")
    st.markdown(
        '<p class="scenario-description">Analyze emails and draft intelligent responses with real-time web research</p>',
        unsafe_allow_html=True,
    )

    # Sample email template
    if st.checkbox("📝 Load Sample Email (Acme Ventures)"):
        sample_email = """From: sarah.chen@acmeventures.com
To: you@yourcompany.com
Subject: Series A Funding Discussion - Next Steps

Dear Team,

I hope this email finds you well. My name is Sarah Chen, and I'm a Partner at Acme Ventures.

We've been tracking your company's progress over the past few months, and we're very impressed with the traction you've achieved in the AI automation space. Your approach to solving enterprise workflow problems aligns well with our investment thesis.

We'd love to schedule a meeting to discuss potential Series A funding opportunities. Would you be available for a call next week to explore how we might work together?

Looking forward to hearing from you.

Best regards,
Sarah Chen
Partner, Acme Ventures"""
    else:
        sample_email = ""

    email_text = st.text_area(
        "**Paste email content here:**",
        value=sample_email,
        height=300,
        placeholder="From: investor@company.com\nSubject: ...\n\nEmail content here...",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🔍 Analyze Email & Draft Reply", type="primary", use_container_width=True
        )

    if analyze_button and email_text:
        with st.spinner("🤖 Agent is working... This may take 10-15 seconds"):
            try:
                # Import and call agent
                from src.agents.orchestrator import AgentOrchestrator

                agent = AgentOrchestrator()

                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("🔍 Analyzing email content...")
                progress_bar.progress(20)

                status_text.text("🌐 Researching entities with Linkup...")
                progress_bar.progress(50)

                result = agent.process(
                    scenario="email", input_data={"email_content": email_text}
                )

                status_text.text("✍️ Drafting intelligent response...")
                progress_bar.progress(80)

                status_text.text("✅ Complete!")
                progress_bar.progress(100)

                st.session_state.current_result = result
                st.session_state.analysis_complete = True

                # Clear progress indicators
                status_text.empty()
                progress_bar.empty()

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Make sure Developer 1 has implemented the email agent!")

    # Display results
    if st.session_state.analysis_complete and st.session_state.current_result:
        result = st.session_state.current_result

        st.success(f"✅ Analysis complete in {result.get('execution_time', 0)}s")

        # Reasoning steps
        with st.expander("🧠 Agent Reasoning Process", expanded=True):
            display_reasoning_steps(result.get("reasoning_steps", []))

        # Linkup sources
        with st.expander("🔍 Web Research Sources", expanded=True):
            display_linkup_sources(result.get("linkup_sources", []))

        # Draft reply
        st.markdown("### 📝 Generated Email Reply")
        confidence_score = result.get("confidence", 0)

        # Confidence badge with color coding
        if confidence_score >= 0.8:
            badge_color = "🟢"
            confidence_text = "High"
        elif confidence_score >= 0.6:
            badge_color = "🟡"
            confidence_text = "Medium"
        else:
            badge_color = "🔴"
            confidence_text = "Low"

        st.markdown(
            f"**{badge_color} Confidence Score:** {confidence_score:.0%} ({confidence_text})"
        )

        draft_reply = result.get(
            "draft_reply", result.get("result", "No reply generated")
        )

        # Display formatted reply
        st.markdown('<div class="result-card">', unsafe_allow_html=True)

        # Convert newlines to proper HTML breaks and add paragraph spacing
        formatted_html = draft_reply.replace(
            "\n\n", '</p><p style="margin-top: 16px;">'
        ).replace("\n", "<br>")
        if not formatted_html.startswith("<p"):
            formatted_html = f"<p>{formatted_html}</p>"

        st.markdown(
            f"""
<div style="line-height: 2.0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 15px; white-space: pre-wrap;">
{formatted_html}
</div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Editable version in expander
        with st.expander("✏️ Edit Reply (if needed)"):
            draft_reply = st.text_area(
                "You can edit this before sending:",
                value=draft_reply,
                height=300,
                key="email_draft",
            )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.code(draft_reply, language=None)
                st.success("✅ Reply copied! (Use Ctrl+C from the box above)")
        with col2:
            if st.button("📧 Send Email", use_container_width=True):
                st.info(
                    "📧 Email ready to send! Copy above and paste into your email client."
                )
        with col3:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.analysis_complete = False
                st.rerun()

# ==================== SCENARIO 2: DOCUMENT ANALYSIS ====================
elif scenario == "📄 Document Analysis":
    st.markdown("## 📄 Document Analysis & Verification")
    st.markdown(
        '<p class="scenario-description">Upload contracts and verify clauses against industry standards using Linkup</p>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "**Upload PDF Contract:**",
        type=["pdf"],
        help="Upload a PDF contract for analysis",
    )

    question = st.text_input(
        "**What would you like to analyze?**",
        value="Are these payment terms standard for 2025 SaaS contracts?",
        placeholder="e.g., Are payment terms standard? Review termination clauses.",
    )

    if uploaded_file and question:
        # Show file info
        st.info(
            f"📄 File uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)"
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_doc_button = st.button(
                "🔍 Analyze Document", type="primary", use_container_width=True
            )

        if analyze_doc_button:
            with st.spinner(
                "📄 Extracting and analyzing document... This may take 15-20 seconds"
            ):
                try:
                    # Save uploaded file temporarily
                    import tempfile

                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".pdf"
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    # Import and call agent
                    from src.agents.orchestrator import AgentOrchestrator

                    agent = AgentOrchestrator()

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.text("📄 Extracting text from PDF...")
                    progress_bar.progress(25)

                    status_text.text("🔍 Identifying key clauses...")
                    progress_bar.progress(50)

                    status_text.text("🌐 Researching industry standards with Linkup...")
                    progress_bar.progress(75)

                    result = agent.process(
                        scenario="document",
                        input_data={"file_path": tmp_file_path, "question": question},
                    )

                    status_text.text("✅ Complete!")
                    progress_bar.progress(100)

                    st.session_state.current_result = result
                    st.session_state.analysis_complete = True

                    status_text.empty()
                    progress_bar.empty()

                    # Clean up temp file
                    os.unlink(tmp_file_path)

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info(
                        "💡 Make sure Developer 1 has implemented the document agent!"
                    )

    # Display results
    if st.session_state.analysis_complete and st.session_state.current_result:
        result = st.session_state.current_result

        st.success(f"✅ Analysis complete in {result.get('execution_time', 0)}s")

        # Reasoning steps
        with st.expander("🧠 Agent Reasoning Process", expanded=True):
            display_reasoning_steps(result.get("reasoning_steps", []))

        # Linkup sources
        with st.expander("🔍 Industry Standards Research", expanded=True):
            display_linkup_sources(result.get("linkup_sources", []))

        # Analysis results
        st.markdown("### 📊 Document Analysis Results")

        # Display result (could be structured data)
        analysis_text = result.get("result", "No analysis generated")

        # Try to parse if it's structured
        if isinstance(analysis_text, dict):
            for key, value in analysis_text.items():
                st.markdown(f"**{key}:** {value}")
        else:
            st.markdown(
                f'<div class="result-card">{analysis_text}</div>',
                unsafe_allow_html=True,
            )

        # Warning flags (if any)
        if "warnings" in result:
            st.markdown("### ⚠️ Flagged Issues")
            for warning in result["warnings"]:
                st.markdown(
                    f'<div class="warning-card">⚠️ {warning}</div>',
                    unsafe_allow_html=True,
                )

        if st.button("🔄 Analyze Another Document"):
            st.session_state.analysis_complete = False
            st.rerun()

# ==================== SCENARIO 3: MEETING PREPARATION ====================
elif scenario == "📅 Meeting Preparation":
    st.markdown("## 📅 Meeting Preparation Assistant")
    st.markdown(
        '<p class="scenario-description">Generate comprehensive meeting briefings with past context and real-time research</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input(
            "**Company Name:**", placeholder="e.g., TechCorp", value="TechCorp"
        )

    with col2:
        meeting_date = st.text_input(
            "**Meeting Date/Time:**",
            placeholder="e.g., Tomorrow at 3pm",
            value="Tomorrow at 3pm",
        )

    meeting_context = st.text_area(
        "**Meeting Context (optional):**",
        placeholder="e.g., Partnership discussion for AI integration, follow-up from initial call",
        height=100,
        value="Partnership discussion for AI integration",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        prep_button = st.button(
            "📋 Generate Meeting Briefing", type="primary", use_container_width=True
        )

    if prep_button and company_name:
        with st.spinner(
            "📋 Preparing comprehensive briefing... This may take 15-20 seconds"
        ):
            try:
                # Import and call agent
                from src.agents.orchestrator import AgentOrchestrator

                agent = AgentOrchestrator()

                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("🔍 Searching past interactions...")
                progress_bar.progress(25)

                status_text.text("🌐 Researching current company news with Linkup...")
                progress_bar.progress(50)

                status_text.text("📊 Analyzing and synthesizing information...")
                progress_bar.progress(75)

                result = agent.process(
                    scenario="meeting",
                    input_data={
                        "company_name": company_name,
                        "meeting_context": meeting_context,
                        "meeting_date": meeting_date,
                    },
                )

                status_text.text("✅ Complete!")
                progress_bar.progress(100)

                st.session_state.current_result = result
                st.session_state.analysis_complete = True

                status_text.empty()
                progress_bar.empty()

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Make sure Developer 1 has implemented the meeting agent!")

    # Display results
    if st.session_state.analysis_complete and st.session_state.current_result:
        result = st.session_state.current_result

        st.success(f"✅ Briefing ready in {result.get('execution_time', 0)}s")

        # Reasoning steps
        with st.expander("🧠 Agent Reasoning Process", expanded=True):
            display_reasoning_steps(result.get("reasoning_steps", []))

        # Linkup sources
        with st.expander("🔍 Current News & Research", expanded=True):
            display_linkup_sources(result.get("linkup_sources", []))

        # Meeting briefing
        st.markdown("### 📋 Meeting Briefing")
        st.markdown(f"**Meeting with:** {company_name}")
        st.markdown(f"**When:** {meeting_date}")

        briefing_text = result.get("result", "No briefing generated")

        st.markdown(
            f'<div class="result-card">{briefing_text}</div>', unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Briefing"):
                st.download_button(
                    label="📥 Download as Text File",
                    data=briefing_text,
                    file_name=f"meeting_briefing_{company_name}.txt",
                    mime="text/plain",
                )
        with col2:
            if st.button("🔄 Generate New Briefing"):
                st.session_state.analysis_complete = False
                st.rerun()

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🚀 Built with Streamlit")
with col2:
    st.caption("🤖 Powered by Llama 3.3 70B (Groq)")
with col3:
    st.caption("🔍 Research via Linkup")
