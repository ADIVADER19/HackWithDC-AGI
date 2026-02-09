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
if scenario == "🤖 PDF Chatbot":
    from src.ui.components.chatbot_ui import render_chatbot_ui
    render_chatbot_ui()
# ...existing code for other scenarios...
