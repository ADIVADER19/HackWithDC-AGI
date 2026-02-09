#!/usr/bin/env python3
"""Test Linkup API connection"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config/.env")

api_key = os.getenv("LINKUP_API_KEY")
print(f"✓ API Key loaded: {api_key[:20]}...")

# Test import
try:
    from linkup import LinkupClient

    print("✓ LinkupClient imported successfully")

    # Initialize client
    print("\n📡 Testing Linkup API connection...")
    client = LinkupClient(api_key=api_key)

    # Make a search query
    result = client.search(
        query="artificial intelligence", depth="standard", output_type="searchResults"
    )

    print("✅ Linkup API connection successful!")
    print(f"\nResult type: {type(result)}")

    if isinstance(result, dict):
        print(f"Response keys: {list(result.keys())}")
        if "results" in result:
            print(f"Number of search results: {len(result['results'])}")
            if result["results"]:
                print(f"\nFirst result:")
                first = result["results"][0]
                for key in ["title", "url", "snippet"]:
                    if key in first:
                        val = first[key]
                        if len(str(val)) > 60:
                            print(f"  {key}: {str(val)[:60]}...")
                        else:
                            print(f"  {key}: {val}")

except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")
    import traceback

    traceback.print_exc()
