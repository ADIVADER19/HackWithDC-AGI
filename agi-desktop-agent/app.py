"""
Email Intelligence Agent - Streamlit UI
Interactive interface to test email analysis with Smart Linkup Usage
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "config"))

import streamlit as st
from datetime import datetime
import json

from agents.email_intelligence_agent import EmailIntelligenceAgent
from tests.demo_data.sample_emails import DEMO_EMAILS, list_demo_emails

# Page configuration
st.set_page_config(
    page_title="Email Intelligence Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown(
    """
<style>
    .main { padding: 0rem 1rem; }
    .entity-badge {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        margin: 0.2rem;
        border-radius: 0.3rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .entity-company {
        background-color: #e3f2fd;
        color: #1565c0;
    }
    .entity-person {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    .entity-product {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .source-card {
        background-color: #fafafa;
        padding: 0.8rem;
        border-left: 4px solid #2196F3;
        margin: 0.5rem 0;
        border-radius: 0.2rem;
    }
    .efficiency-high {
        color: #2e7d32;
        font-weight: bold;
    }
    .efficiency-medium {
        color: #f57c00;
        font-weight: bold;
    }
    .efficiency-low {
        color: #c62828;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)


def format_entity_badge(entity_name: str, entity_type: str) -> str:
    """Format entity as styled badge"""
    type_class = {
        "company": "entity-company",
        "person": "entity-person",
        "product": "entity-product",
    }.get(entity_type.lower(), "entity-company")

    return f'<span class="entity-badge {type_class}">{entity_name} <small>({entity_type})</small></span>'


def format_efficiency(efficiency_pct: float) -> str:
    """Format efficiency metric with color"""
    if efficiency_pct >= 70:
        css_class = "efficiency-high"
    elif efficiency_pct >= 40:
        css_class = "efficiency-medium"
    else:
        css_class = "efficiency-low"

    return f'<span class="{css_class}">{efficiency_pct:.1f}%</span>'


def main():
    # Header
    st.title("📧 Email Intelligence Agent")
    st.markdown("*Analyze emails with smart research and intelligent reply generation*")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        mode = st.radio(
            "Select Input Mode:",
            ["Use Demo Email", "Paste Custom Email"],
            help="Choose how to input the email",
        )

        st.markdown("---")
        st.markdown("### 🚀 About Smart Linkup Usage")
        st.markdown(
            """
        This agent intelligently decides when to search:
        - **Known entities** (Google, Microsoft) → Use existing knowledge
        - **Unknown entities** (startups) → Execute web search
        - **Mixed** → Hybrid approach for optimal cost/quality
        
        **Result**: 75% fewer API calls while maintaining quality
        """
        )

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Email Input")

        if mode == "Use Demo Email":
            demo_options = list_demo_emails()
            selected_demo = st.selectbox(
                "Choose a demo email:",
                demo_options,
                help="Select from sample business emails",
            )

            email_data = DEMO_EMAILS[selected_demo]
            email_content = email_data["content"]
            email_metadata = email_data.get("metadata", {})

            # Display email preview
            with st.expander("📧 Email Preview", expanded=True):
                st.markdown(f"**From:** {email_data.get('from', 'Unknown')}")
                st.markdown(f"**Subject:** {email_data.get('subject', 'No Subject')}")
                st.markdown(f"**Date:** {email_data.get('date', 'Unknown')}")
                st.markdown("---")
                st.text(email_content)

        else:
            email_content = st.text_area(
                "Paste your email content:",
                height=250,
                placeholder="Enter the email text here...",
                help="Paste the email you want to analyze",
            )
            email_metadata = {
                "from": st.text_input("From (optional):", ""),
                "subject": st.text_input("Subject (optional):", ""),
                "date": datetime.now().isoformat(),
            }

    with col2:
        st.subheader("🎛️ Options")

        show_reasoning = st.checkbox(
            "Show reasoning steps", value=True, help="Display decision-making process"
        )

        show_all_sources = st.checkbox(
            "Show all sources", value=False, help="Display all sources vs top 3"
        )

        st.markdown("---")

        # Analysis button
        if st.button("🔍 Analyze Email", use_container_width=True, type="primary"):
            st.session_state.run_analysis = True

    # Run analysis if button clicked
    if st.session_state.get("run_analysis"):
        if mode == "Paste Custom Email" and not email_content.strip():
            st.error("❌ Please enter email content")
        else:
            with st.spinner("🔄 Analyzing email..."):
                try:
                    # Initialize agent
                    agent = EmailIntelligenceAgent()

                    # Analyze email
                    result = agent.analyze_email(email_content, email_metadata)

                    # Store result in session state
                    st.session_state.last_result = result
                    st.session_state.run_analysis = False

                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    import traceback

                    st.error(traceback.format_exc())

    # Display results if available
    if st.session_state.get("last_result"):
        result = st.session_state.last_result

        st.markdown("---")
        st.subheader("📊 Analysis Results")

        # Metrics row
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

        stats = result.get("stats", {})
        with metrics_col1:
            st.metric("Total Entities", stats.get("total_entities", 0))
        with metrics_col2:
            st.metric("Searched (Linkup)", stats.get("entities_searched", 0))
        with metrics_col3:
            st.metric("Using Knowledge", stats.get("entities_known", 0))
        with metrics_col4:
            efficiency = stats.get("efficiency_pct", 0)
            st.metric("Efficiency", f"{efficiency:.1f}%")

        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["🔍 Entities", "📚 Research", "✍️ Reply", "🧠 Reasoning", "📈 Stats"]
        )

        # Tab 1: Entities
        with tab1:
            st.subheader("Extracted Entities")
            entities = result.get("entities", [])

            if entities:
                for i, entity in enumerate(entities, 1):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(
                            f"{i}. {format_entity_badge(entity['name'], entity['type'])}",
                            unsafe_allow_html=True,
                        )
                        if entity.get("context"):
                            st.caption(f"Context: {entity['context']}")
                    with col2:
                        st.caption(f"Type: {entity.get('type', 'unknown').upper()}")
            else:
                st.info("No entities found in email")

        # Tab 2: Research
        with tab2:
            st.subheader("Research Findings")
            research_data = result.get("research", {})

            if research_data:
                for entity_name, data in research_data.items():
                    with st.expander(f"🔎 {entity_name}", expanded=True):
                        # Check source type
                        if data.get("used_existing_knowledge"):
                            st.success("✓ Source: Existing Knowledge")
                            st.write(f"**Info:** {data.get('known_info', 'N/A')}")
                            st.caption(f"Reasoning: {data.get('reasoning', 'N/A')}")
                        else:
                            sources = data.get("sources", [])
                            if sources:
                                st.info(f"🔍 Found {len(sources)} sources from Linkup")
                                num_to_show = (
                                    len(sources)
                                    if show_all_sources
                                    else min(3, len(sources))
                                )
                                for j, source in enumerate(sources[:num_to_show], 1):
                                    st.markdown(
                                        f"**{j}. {source.get('title', 'No title')}**"
                                    )
                                    st.caption(
                                        f"URL: {source.get('url', 'N/A')[:80]}..."
                                    )
                                    st.write(
                                        source.get("snippet", "No snippet")[:200]
                                        + "..."
                                    )
                                    st.divider()
                            elif data.get("error"):
                                st.warning(f"⚠️ Error: {data.get('error')}")
                            else:
                                st.info("No sources found")
            else:
                st.info("No research conducted")

        # Tab 3: Reply
        with tab3:
            st.subheader("Drafted Reply")
            draft_reply = result.get("draft_reply", "")

            if draft_reply and draft_reply != "Error: Could not generate reply":
                st.write(draft_reply)

                # Copy button
                st.code(draft_reply, language="text", line_numbers=False)
            else:
                st.warning("Could not generate reply")

        # Tab 4: Reasoning
        with tab4:
            st.subheader("Decision-Making Steps")
            reasoning_steps = result.get("reasoning_steps", [])

            if reasoning_steps and show_reasoning:
                for step in reasoning_steps:
                    # Determine icon based on step type
                    icon = "🧠"
                    if "✓" in step.get("step", ""):
                        icon = "✅"
                    elif "❌" in step.get("step", ""):
                        icon = "❌"
                    elif "⚠️" in step.get("step", ""):
                        icon = "⚠️"
                    elif "🔍" in step.get("step", ""):
                        icon = "🔍"
                    elif "🚀" in step.get("step", ""):
                        icon = "🚀"

                    st.write(
                        f"{icon} **[{step.get('timestamp', 'N/A')}]** {step.get('step', '')}"
                    )
            elif show_reasoning:
                st.info("No reasoning steps available")
            else:
                st.info("Reasoning display disabled in sidebar")

        # Tab 5: Stats
        with tab5:
            st.subheader("📊 Detailed Statistics")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Processing Metrics")
                st.write(
                    f"**Execution Time:** {result.get('execution_time', 'N/A'):.2f}s"
                )
                st.write(f"**Total Sources:** {len(result.get('sources', []))}")
                st.write(f"**Timestamp:** {result.get('timestamp', 'N/A')}")

            with col2:
                st.markdown("### Smart Linkup Impact")
                if stats:
                    col1_inner, col2_inner = st.columns(2)
                    with col1_inner:
                        st.markdown(
                            f"**Total Entities:** {stats.get('total_entities', 0)}"
                        )
                        st.markdown(
                            f"**Searched:** {stats.get('entities_searched', 0)}"
                        )
                    with col2_inner:
                        st.markdown(f"**Known:** {stats.get('entities_known', 0)}")
                        st.markdown(f"**Sources:** {stats.get('linkup_sources', 0)}")

                    efficiency = stats.get("efficiency_pct", 0)
                    st.markdown(f"### Efficiency")

                    # Progress bar
                    st.progress(efficiency / 100)

                    st.markdown(
                        f"**{efficiency:.1f}%** of entities used existing knowledge"
                    )

                    # Cost estimation
                    searches_avoided = stats.get("entities_known", 0)
                    if searches_avoided > 0:
                        estimated_savings = searches_avoided * 0.01
                        st.success(
                            f"💰 **Estimated Savings:** ${estimated_savings:.2f} (skipped {searches_avoided} API calls)"
                        )

        # Download results
        st.markdown("---")
        st.subheader("📥 Export Results")

        col1, col2 = st.columns(2)

        with col1:
            json_str = json.dumps(result, indent=2, default=str)
            st.download_button(
                label="📄 Download JSON",
                data=json_str,
                file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )

        with col2:
            txt_content = f"""EMAIL ANALYSIS REPORT
Generated: {result.get('timestamp')}

ENTITIES EXTRACTED:
{chr(10).join([f"- {e['name']} ({e['type']})" for e in result.get('entities', [])])}

SMART LINKUP STATS:
- Total Entities: {stats.get('total_entities', 0)}
- Searched: {stats.get('entities_searched', 0)}
- Using Knowledge: {stats.get('entities_known', 0)}
- Efficiency: {stats.get('efficiency_pct', 0):.1f}%

DRAFTED REPLY:
{result.get('draft_reply', 'N/A')}
"""
            st.download_button(
                label="📝 Download Text",
                data=txt_content,
                file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
            )


if __name__ == "__main__":
    # Initialize session state
    if "run_analysis" not in st.session_state:
        st.session_state.run_analysis = False
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    main()
