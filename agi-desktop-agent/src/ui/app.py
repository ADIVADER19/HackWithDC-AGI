"""
AGI Desktop Intelligence Agent - Main Streamlit App
Developer 2: Desktop UI
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Page configuration
st.set_page_config(
    page_title="AGI Desktop Intelligence Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a73e8;
        text-align: center;
        margin-bottom: 2rem;
    }
    .scenario-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1a73e8;
    }
    .source-card {
        background-color: #e8f0fe;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1a73e8/ffffff?text=AGI+Agent", width=150)
    st.title("Navigation")
    
    scenario = st.radio(
        "Choose Scenario",
        ["🎯 Quick Start", "📧 Email Intelligence", "📄 Document Analysis", "📅 Meeting Preparation"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.caption("AGI-Inspired Desktop Agent powered by Llama 3.3 70B and Linkup")
    
    st.markdown("---")
    st.markdown("### Status")
    # TODO: Add connection status indicators
    st.success("✅ Groq API")
    st.success("✅ Linkup API")

# Main content
st.markdown('<div class="main-header">🤖 AGI Desktop Intelligence Agent</div>', unsafe_allow_html=True)

# Route to appropriate scenario
if scenario == "🎯 Quick Start":
    st.markdown("""
    ### Welcome! Choose a scenario from the sidebar:
    
    - **📧 Email Intelligence**: Analyze emails and draft intelligent responses using real-time web research
    - **📄 Document Analysis**: Extract and verify contract clauses against industry standards
    - **📅 Meeting Preparation**: Generate comprehensive briefings with past context and current news
    
    ### How it works:
    1. Select a scenario from the sidebar
    2. Provide your input (email text, document, or meeting info)
    3. The agent will research using Linkup and generate results
    4. Review the reasoning steps and sources
    """)
    
    st.info("👈 Select a scenario from the sidebar to get started")

elif scenario == "📧 Email Intelligence":
    st.header("📧 Email Intelligence")
    st.markdown("Analyze emails and draft intelligent responses with real-time research")
    
    # TODO: Import email_ui component when ready
    # For now, placeholder UI
    
    email_text = st.text_area(
        "Paste email content here:",
        height=200,
        placeholder="From: investor@acmeventures.com\nSubject: Series A Discussion\n\nHi, we're interested in discussing your Series A round..."
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze Email", use_container_width=True, type="primary")
    
    if analyze_button and email_text:
        with st.spinner("Analyzing email and researching..."):
            # TODO: Call agent orchestrator
            # from src.agents.orchestrator import AgentOrchestrator
            # agent = AgentOrchestrator()
            # result = agent.process(scenario="email", input_data={"email_content": email_text})
            
            # Placeholder result
            st.success("✅ Analysis complete!")
            
            # Reasoning steps
            with st.expander("🧠 Reasoning Process", expanded=True):
                st.write("1. Analyzing email content...")
                st.write("2. Detected entity: Acme Ventures")
                st.write("3. Searching Linkup for company info...")
                st.write("4. Drafting informed response...")
            
            # Linkup sources
            with st.expander("🔍 Web Research Sources"):
                st.markdown("""
                <div class="source-card">
                <strong>Acme Ventures - Recent Investments</strong><br>
                Acme Ventures recently invested in 3 AI startups...<br>
                <a href="https://example.com">View Source</a>
                </div>
                """, unsafe_allow_html=True)
            
            # Draft reply
            st.subheader("📝 Draft Reply")
            st.text_area(
                "Generated response:",
                value="Dear [Investor Name],\n\nThank you for your interest in our Series A round...",
                height=300
            )

elif scenario == "📄 Document Analysis":
    st.header("📄 Document Analysis")
    st.markdown("Upload a PDF contract and verify clauses against industry standards")
    
    uploaded_file = st.file_uploader("Upload PDF contract", type=['pdf'])
    
    if uploaded_file:
        question = st.text_input(
            "What would you like to analyze?",
            placeholder="Are the payment terms standard for SaaS contracts?"
        )
        
        if st.button("🔍 Analyze Document", type="primary"):
            with st.spinner("Extracting and analyzing document..."):
                # TODO: Call document agent
                st.success("✅ Analysis complete!")
                
                st.subheader("📊 Analysis Results")
                st.write("Payment Terms: Net-60 ⚠️ (Industry standard: Net-30)")

elif scenario == "📅 Meeting Preparation":
    st.header("📅 Meeting Preparation")
    st.markdown("Generate comprehensive meeting briefings with context and research")
    
    company_name = st.text_input("Company name:", placeholder="TechCorp")
    meeting_context = st.text_area(
        "Meeting context:",
        placeholder="Partnership discussion for AI integration",
        height=100
    )
    
    if st.button("📋 Generate Briefing", type="primary"):
        if company_name:
            with st.spinner("Preparing briefing..."):
                # TODO: Call meeting agent
                st.success("✅ Briefing ready!")
                
                st.subheader("📋 Meeting Briefing")
                st.markdown("""
                **Past Interactions:**
                - Last contact: 2 months ago
                - Topic: Initial partnership exploration
                
                **Recent News:**
                - TechCorp raised Series B ($50M)
                - Launched new AI product
                
                **Talking Points:**
                - Reference their new AI product
                - Discuss synergies with our platform
                """)

# Footer
st.markdown("---")
st.caption("Built with Streamlit • Powered by Llama 3.3 70B + Linkup")
