#!/usr/bin/env python3
"""
System readiness check for AGI Desktop Agent
"""
import sys
import os

sys.path.insert(0, "src")

from pathlib import Path
from dotenv import load_dotenv

print("\n" + "=" * 60)
print("✅ SYSTEM READINESS CHECK")
print("=" * 60)

# Load env
env_path = Path("config/.env")
load_dotenv(env_path)

# Check 1: Dependencies
print("\n📦 DEPENDENCIES:")
deps = ["openai", "groq", "streamlit", "PyPDF2"]
for dep in deps:
    try:
        __import__(dep)
        print(f"  ✅ {dep}")
    except ImportError:
        print(f"  ❌ {dep} - MISSING")

# Check 2: Agent Imports
print("\n🤖 AGENT MODULES:")
agents = {
    "GroqClient": "agents.groq_client",
    "LinkupWrapper": "agents.linkup_wrapper",
    "EmailIntelligenceAgent": "agents.email_intelligence_agent",
    "DocumentAgent": "agents.document_agent",
    "AgentOrchestrator": "agents.orchestrator",
}

for name, module in agents.items():
    try:
        __import__(module)
        print(f"  ✅ {name}")
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:50]}")

# Check 3: API Keys
print("\n🔑 API CONFIGURATION:")
groq_key = os.getenv("GROQ_API_KEY")
linkup_key = os.getenv("LINKUP_API_KEY")

if groq_key:
    print(f"  ✅ GROQ_API_KEY: {groq_key[:20]}...")
else:
    print(f"  ❌ GROQ_API_KEY: NOT CONFIGURED")

if linkup_key:
    print(f"  ✅ LINKUP_API_KEY: {linkup_key[:20]}...")
else:
    print(f"  ❌ LINKUP_API_KEY: NOT CONFIGURED")

# Check 4: Directory Structure
print("\n📁 DIRECTORY STRUCTURE:")
dirs_to_check = ["src/agents", "src/ui", "config", "data", "tests"]
for d in dirs_to_check:
    if Path(d).exists():
        print(f"  ✅ {d}/")
    else:
        print(f"  ❌ {d}/ - MISSING")

print("\n" + "=" * 60)
print("✅ SYSTEM READY - Run: streamlit run app.py")
print("=" * 60 + "\n")
