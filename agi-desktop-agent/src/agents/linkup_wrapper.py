"""
Linkup Search API Wrapper
Developer 1: Backend Agents
"""

import os
from linkup import LinkupClient
from dotenv import load_dotenv

# Use absolute path so it works regardless of cwd
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
load_dotenv(os.path.join(_project_root, 'config', '.env'))


class LinkupWrapper:
    def __init__(self):
        self.api_key = os.getenv("LINKUP_API_KEY")
        self.client = LinkupClient(api_key=self.api_key)
        self.depth = os.getenv("LINKUP_DEPTH", "standard")
        self.output_type = os.getenv("LINKUP_OUTPUT_TYPE", "searchResults")

    def search(self, query, max_results=5):
        """
        Search the web using Linkup

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            dict with sources, snippets, and URLs
        """
        try:
            # Execute Linkup search
            results = self.client.search(
                query=query, depth=self.depth, output_type=self.output_type
            )

            # Parse and format results from LinkupSearchResults object
            formatted_sources = []

            if hasattr(results, "results") and results.results:
                for i, result in enumerate(results.results[:max_results]):
                    # Extract data from LinkupSearchTextResult or similar objects
                    source_item = {
                        "title": getattr(result, "name", "") or getattr(result, "title", ""),
                        "url": getattr(result, "url", ""),
                        "snippet": getattr(
                            result, "snippet", getattr(result, "content", "")
                        )[:200],
                        "relevance": i + 1,
                    }
                    formatted_sources.append(source_item)

            return {
                "query": query,
                "sources": formatted_sources,
                "total_found": len(formatted_sources),
            }

        except Exception as e:
            print(f"Linkup Search Error: {e}")
            return {"query": query, "sources": [], "error": str(e)}

    def format_sources_for_agent(self, sources):
        """Format Linkup sources into text for LLM context"""
        formatted = []
        for i, source in enumerate(sources, 1):
            formatted.append(
                f"Source {i}: {source['title']}\n"
                f"URL: {source['url']}\n"
                f"Content: {source['snippet']}\n"
            )
        return "\n".join(formatted)

    def test_connection(self):
        """Test if Linkup API is working"""
        test_result = self.search("test query", max_results=1)
        return len(test_result.get("sources", [])) > 0 or "error" not in test_result


# Quick test
if __name__ == "__main__":
    linkup = LinkupWrapper()
    if linkup.test_connection():
        print("Linkup API connection successful!")
        # Test search
        results = linkup.search("Anthropic AI company", max_results=3)
        print(f"Found {results['total_found']} results")
        for source in results["sources"]:
            print(f"- {source['title']}")
    else:
        print("Linkup API connection failed")
