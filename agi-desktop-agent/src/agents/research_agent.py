"""Research agent using Linkup API for web search"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to ensure config is loaded
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from linkup import LinkupClient

# Load environment variables from config directory
env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)


class ResearchAgent:
    """Perform research using Linkup API"""

    def __init__(self):
        """Initialize the research agent with Linkup client"""
        self.client = LinkupClient(api_key=os.getenv("LINKUP_API_KEY"))
        self.depth = os.getenv("LINKUP_DEPTH", "standard")
        self.output_type = os.getenv("LINKUP_OUTPUT_TYPE", "searchResults")

    def search(self, query: str, depth: str = None) -> dict:
        """Execute a web search using Linkup API"""

        if depth is None:
            depth = self.depth

        try:
            print(f"   🔍 Searching: '{query}'...")

            result = self.client.search(
                query=query, depth=depth, output_type=self.output_type
            )

            # Convert to dict format
            search_result = {
                "query": query,
                "depth": depth,
                "timestamp": datetime.now().isoformat(),
                "results": [],
            }

            if hasattr(result, "results") and result.results:
                for item in result.results:
                    result_item = {
                        "type": type(item).__name__,
                        "url": getattr(item, "url", None),
                        "title": getattr(item, "title", None),
                    }

                    # Add content/snippet if available
                    if hasattr(item, "content"):
                        result_item["content"] = item.content
                    elif hasattr(item, "snippet"):
                        result_item["snippet"] = item.snippet

                    search_result["results"].append(result_item)

                print(f"   ✓ Found {len(search_result['results'])} results")
                return search_result

            return search_result

        except Exception as e:
            print(f"   ❌ Search error: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def research_topics(self, queries: list) -> dict:
        """Research multiple related topics"""

        research_results = {
            "queries": queries,
            "timestamp": datetime.now().isoformat(),
            "results": {},
        }

        for query in queries:
            result = self.search(query)
            research_results["results"][query] = result

        return research_results

    def format_for_display(self, search_result: dict) -> str:
        """Format search results for display"""
        output = []
        output.append(f"\n{'='*70}")
        output.append(f"🔍 SEARCH RESULTS FOR: '{search_result.get('query')}'")
        output.append(f"{'='*70}")

        if "error" in search_result:
            output.append(f"❌ ERROR: {search_result['error']}")
            return "\n".join(output)

        results = search_result.get("results", [])
        output.append(f"Found {len(results)} results:\n")

        for i, result in enumerate(results[:5], 1):  # Show top 5
            output.append(f"{i}. {result.get('title', 'No title')}")
            output.append(f"   URL: {result.get('url', 'N/A')}")
            if result.get("snippet"):
                snippet = result["snippet"][:100]
                output.append(f"   📝 {snippet}...")
            output.append("")

        output.append(f"{'='*70}")
        return "\n".join(output)

    def summarize_research(self, research_results: dict) -> str:
        """Create a summary of research findings"""
        summary = []
        summary.append("\n📚 RESEARCH SUMMARY")
        summary.append("=" * 70)

        for query, result in research_results.get("results", {}).items():
            if "error" not in result:
                num_results = len(result.get("results", []))
                summary.append(f"\n🔹 {query}")
                summary.append(f"   Found {num_results} sources")

                # Show top 3 sources
                for i, item in enumerate(result.get("results", [])[:3], 1):
                    summary.append(f"   {i}. {item.get('title', 'N/A')}")

        summary.append("\n" + "=" * 70)
        return "\n".join(summary)


if __name__ == "__main__":
    from email_processor import EmailProcessor
    from sample_emails import get_sample_emails

    print("🚀 Research Agent - Web Search Demo\n")

    # Get sample email and extract research queries
    processor = EmailProcessor()
    email = get_sample_emails()[0]  # First email

    print(f"Processing email: {email['subject']}\n")
    extracted = processor.extract_entities(email)

    # Research the queries
    if "research_queries" in extracted:
        agent = ResearchAgent()
        print(f"📚 Researching {len(extracted['research_queries'])} topics...\n")

        research = agent.research_topics(extracted["research_queries"])

        # Display results
        for query, result in research["results"].items():
            print(agent.format_for_display(result))

        # Show summary
        print(agent.summarize_research(research))
