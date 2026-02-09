"""
Email Intelligence Agent
Developer 1: Backend Agents

This agent analyzes emails, researches entities using Linkup, and drafts informed replies.
"""

import json
import time
import re
from typing import List, Dict, Any
from .groq_client import GroqClient
from .linkup_wrapper import LinkupWrapper


class EmailIntelligenceAgent:
    def __init__(
        self, groq_client: GroqClient = None, linkup_wrapper: LinkupWrapper = None
    ):
        """
        Initialize Email Agent with AI and search capabilities

        Args:
            groq_client: GroqClient instance (creates new if None)
            linkup_wrapper: LinkupWrapper instance (creates new if None)
        """
        self.groq = groq_client or GroqClient()
        self.linkup = linkup_wrapper or LinkupWrapper()
        self.reasoning_steps = []
        self.execution_log = []
        self.stats = {
            "total_entities": 0,
            "entities_searched": 0,
            "entities_known": 0,
            "linkup_sources": 0,
        }

    def add_reasoning(self, step: str, level: str = "info"):
        """
        Track reasoning steps for UI display

        Args:
            step: Description of reasoning step
            level: 'info', 'success', 'warning', 'error'
        """
        timestamp = time.strftime("%H:%M:%S")
        self.reasoning_steps.append(
            {"timestamp": timestamp, "step": step, "level": level}
        )
        print(f"🧠 [{timestamp}] {step}")

    def assess_knowledge(
        self, entity: Dict[str, str], email_context: str
    ) -> Dict[str, Any]:
        """
        Intelligently assess if we have sufficient knowledge about an entity
        Decides whether to search Linkup or use existing knowledge

        Args:
            entity: Entity dict with 'name', 'type', 'context'
            email_context: Email content for context

        Returns:
            Assessment with needs_search, reasoning, confidence, known_info
        """
        entity_name = entity.get("name", "")
        entity_type = entity.get("type", "unknown")
        current_date = time.strftime("%Y-%m-%d")

        prompt = f"""Decide if you need current web information about: {entity_name}

Context: {entity.get('context', 'No context')}
Date: {current_date}

BE STRICT. Only search if you MUST have recent 2024-2025 info.

DO NOT SEARCH for:
❌ Generic concepts: "AI", "machine learning", "cloud computing", "real-time processing"
❌ Well-known public companies: Google, Microsoft, Apple, Amazon, OpenAI, Anthropic
❌ Information that's unlikely to change (historical facts, famous people)
❌ Generic terms like "data analytics" or "neural networks"

DO SEARCH for:
✅ Unknown startups or companies (less than 10K Google results)
✅ Specific people if their recent role/achievements matter
✅ Recent funding rounds, acquisitions, partnerships (2024+)
✅ New products or service changes
✅ Companies you're less than 80% confident about

Quick checks FIRST:
1. Do you know this well-known company? → Don't search
2. Is this a generic concept? → Don't search
3. Is this a startup/unknown entity AND relevant to response? → Search

Respond ONLY with JSON:
{{
  "needs_search": true/false,
  "reasoning": "one sentence",
  "confidence": 0.0-1.0,
  "known_info": "what you know",
  "search_query": "exact search string" or null
}}"""

        try:
            response = self.groq.chat(
                messages=[{"role": "user", "content": prompt}], temperature=0.6
            )

            if response.get("error"):
                self.add_reasoning(
                    f"⚠️ Knowledge assessment failed: {response['error']}", "warning"
                )
                # Default to search if assessment fails
                return {
                    "needs_search": True,
                    "reasoning": "Assessment failed, defaulting to search",
                    "confidence": 0.5,
                    "known_info": "",
                    "search_query": entity_name,
                }

            content = response.get("content", "{}").strip()

            # Clean up potential markdown
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()

            assessment = json.loads(content)
            return assessment

        except json.JSONDecodeError as e:
            self.add_reasoning(f"⚠️ Failed to parse assessment: {str(e)}", "warning")
            return {
                "needs_search": True,
                "reasoning": "Parsing error, defaulting to search",
                "confidence": 0.5,
                "known_info": "",
                "search_query": entity_name,
            }
        except Exception as e:
            self.add_reasoning(f"❌ Assessment error: {str(e)}", "error")
            return {
                "needs_search": True,
                "reasoning": "Error occurred, defaulting to search",
                "confidence": 0.5,
                "known_info": "",
                "search_query": entity_name,
            }

    def extract_entities(self, email_content: str) -> List[Dict[str, str]]:
        """
        Extract entities (companies, people, organizations) that need research

        Args:
            email_content: Full email text

        Returns:
            List of entities with type and context
        """
        self.add_reasoning("Step 1: Analyzing email for unknown entities...")

        prompt = f"""Extract entities worth researching from this email.

BE STRICT - Only include:
✅ Unknown companies or startups (worth searching)
✅ Specific people (investors, founders, important contacts)
✅ Specific products that are unclear

DO NOT include:
❌ Well-known companies (Google, Microsoft, Apple, Amazon, OpenAI, Meta, etc.)
❌ Generic terms ("AI", "cloud computing", "real-time data processing", "machine learning")
❌ Broad concepts
❌ The receiver's own company

Email:
{email_content}

Return ONLY JSON array (no markdown):
[
  {{"type": "company", "name": "Acme Ventures", "context": "VC firm from sender"}},
  {{"type": "person", "name": "Alex Chen", "context": "founder/investor"}}
]

If nothing qualifies, return: []"""

        try:
            response = self.groq.chat(
                messages=[{"role": "user", "content": prompt}], temperature=0.3
            )

            if response.get("error"):
                self.add_reasoning(
                    f"⚠️ Entity extraction failed: {response['error']}", "warning"
                )
                return []

            content = response.get("content", "[]")

            # Clean up potential markdown code blocks
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()

            entities = json.loads(content)

            if entities:
                entity_names = ", ".join([e.get("name", "Unknown") for e in entities])
                self.add_reasoning(
                    f"✓ Found {len(entities)} entities: {entity_names}", "success"
                )
            else:
                self.add_reasoning("✓ No entities requiring research", "info")

            return entities

        except json.JSONDecodeError as e:
            self.add_reasoning(f"⚠️ Failed to parse entities: {str(e)}", "warning")
            return []
        except Exception as e:
            self.add_reasoning(f"❌ Entity extraction error: {str(e)}", "error")
            return []

    def research_entity(
        self, entity: Dict[str, str], email_content: str = ""
    ) -> Dict[str, Any]:
        """
        Research a single entity using smart decision-making
        First assesses if we have sufficient knowledge, only searches if needed

        Args:
            entity: Entity dict with 'name', 'type', 'context'
            email_content: Email content for context in assessment

        Returns:
            Research results with sources (or existing knowledge)
        """
        entity_name = entity.get("name", "")
        entity_type = entity.get("type", "unknown")

        # Step 1: Assess knowledge
        self.add_reasoning(
            f"Step 2: Assessing knowledge about '{entity_name}' ({entity_type})..."
        )

        assessment = self.assess_knowledge(entity, email_content)

        # Step 2: Decide based on assessment
        if not assessment.get("needs_search", True):
            # Use existing knowledge
            self.add_reasoning(
                f"✓ Using existing knowledge: {assessment.get('reasoning', 'Sufficient knowledge available')}",
                "success",
            )
            self.stats["entities_known"] += 1

            return {
                "entity": entity_name,
                "type": entity_type,
                "context": entity.get("context", ""),
                "used_existing_knowledge": True,
                "known_info": assessment.get("known_info", ""),
                "reasoning": assessment.get("reasoning", ""),
            }

        # Step 3: Search Linkup for unknown/recent info
        self.add_reasoning(
            f"🔍 External research needed: {assessment.get('reasoning', 'Unknown entity')}",
            "info",
        )
        self.add_reasoning(f"Searching Linkup for '{entity_name}'...")

        search_query = assessment.get("search_query", f"{entity_name} recent news")

        try:
            # Execute Linkup search
            search_results = self.linkup.search(search_query, max_results=5)

            if search_results.get("error"):
                self.add_reasoning(
                    f"⚠️ Search failed for {entity_name}: {search_results['error']}",
                    "warning",
                )
                return {
                    "entity": entity_name,
                    "sources": [],
                    "error": search_results["error"],
                }

            sources = search_results.get("sources", [])
            self.add_reasoning(
                f"✓ Found {len(sources)} sources for {entity_name}", "success"
            )
            self.stats["entities_searched"] += 1
            self.stats["linkup_sources"] += len(sources)

            return {
                "entity": entity_name,
                "type": entity_type,
                "context": entity.get("context", ""),
                "sources": sources,
                "query_used": search_query,
                "used_existing_knowledge": False,
            }

        except Exception as e:
            self.add_reasoning(
                f"❌ Research error for {entity_name}: {str(e)}", "error"
            )
            return {"entity": entity_name, "sources": [], "error": str(e)}

    def research_all_entities(
        self, entities: List[Dict[str, str]], email_content: str = ""
    ) -> Dict[str, Any]:
        """
        Research all extracted entities with smart decision-making
        Uses existing knowledge when sufficient, searches Linkup when needed

        Args:
            entities: List of entity dicts
            email_content: Email content for context in assessments

        Returns:
            Dict mapping entity names to research results
        """
        if not entities:
            return {}

        research_results = {}

        for entity in entities:
            entity_name = entity.get("name", "")
            self.stats["total_entities"] += 1
            research_results[entity_name] = self.research_entity(entity, email_content)

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        return research_results

    def _improve_draft(self, draft: str) -> str:
        """
        Post-process drafted reply to improve quality
        Removes clichés and shortens if too long
        """
        # List of clichés to remove
        cliches = [
            "I hope this email finds you well",
            "hope this message finds you well",
            "testament to our",
            "testament to the",
            "drive innovation",
            "drive growth",
            "looking forward to connecting",
            "looking forward to hearing from you",
            "in closing",
            "in summary",
            "best regards",
            "warm regards",
            "kind regards",
            "please don't hesitate",
            "at your earliest convenience",
            "synergies",
            "strategic partnership",
            "win-win",
        ]

        improved = draft
        for cliche in cliches:
            # Case-insensitive replacement
            import re

            pattern = re.compile(re.escape(cliche), re.IGNORECASE)
            improved = pattern.sub("", improved)

        # Clean up extra spaces
        improved = re.sub(r"\s+", " ", improved).strip()

        # Check word count
        word_count = len(improved.split())
        if word_count > 200:
            # Try to shorten by asking LLM
            self.add_reasoning(
                f"⚠️ Draft is {word_count} words (max 150), attempting to shorten...",
                "warning",
            )

            shorten_prompt = f"""Make this email reply shorter (exactly 100-150 words) while keeping the key points:

{improved}

Shortened version (100-150 words only):"""

            response = self.groq.chat(
                messages=[{"role": "user", "content": shorten_prompt}], temperature=0.5
            )
            if not response.get("error"):
                improved = response.get("content", improved)

        return improved.strip()

    def draft_reply(self, email_content: str, research_data: Dict[str, Any]) -> str:
        """
        Draft an informed reply using research findings or existing knowledge

        Args:
            email_content: Original email text
            research_data: Research results (from Linkup or existing knowledge)

        Returns:
            Drafted reply text
        """
        self.add_reasoning("Step 3: Synthesizing research and drafting reply...")

        # Build research context for the prompt
        research_context = ""
        if research_data:
            research_context = "\n\nRESEARCH FINDINGS & KNOWLEDGE:\n"
            for entity_name, data in research_data.items():
                research_context += f"\n{entity_name}:\n"

                # Handle existing knowledge data
                if data.get("used_existing_knowledge"):
                    research_context += f"[From Existing Knowledge] {data.get('known_info', 'Information available')}\n"
                    if data.get("reasoning"):
                        research_context += f"  Reasoning: {data.get('reasoning')}\n"
                # Handle Linkup search results
                else:
                    sources = data.get("sources", [])
                    if sources:
                        for i, source in enumerate(
                            sources[:3], 1
                        ):  # Top 3 sources per entity
                            research_context += (
                                f"{i}. {source.get('title', 'No title')}\n"
                            )
                            research_context += (
                                f"   {source.get('snippet', 'No content')}\n"
                            )
                    elif data.get("error"):
                        research_context += f"[Search Error] {data.get('error')}\n"

        prompt = f"""Draft a CONCISE, WARM email reply (100-150 words MAXIMUM).

ORIGINAL EMAIL:
{email_content}

{research_context}

TONE RULES:
- Conversational and warm (use contractions: I'm, we're, you're)
- Short sentences and short paragraphs
- NO corporate jargon or clichés (avoid: "I hope this finds you well", "testament to", "drive innovation", "looking forward to")
- Sound human, not like AI wrote it

STRUCTURE:
1. Brief thanks (1-2 sentences)
2. Show you know them (1 sentence with specific research)
3. Express interest + next step (1-2 sentences)

EXAMPLE:
Hi Alex,

Thanks for reaching out! I'm familiar with Acme Ventures' focus on frontier tech—your portfolio of Quantum Labs and CloudScale is impressive.

We'd definitely be interested in exploring a partnership. Our recent Q4 growth aligns well with your investment thesis.

How about Tuesday or Wednesday for a quick call?

Best,
Alex

Now draft the reply (MAXIMUM 150 words):
"""

        try:
            response = self.groq.chat(
                messages=[{"role": "user", "content": prompt}], temperature=0.7
            )

            if response.get("error"):
                self.add_reasoning(
                    f"❌ Reply drafting failed: {response['error']}", "error"
                )
                return "Error: Could not generate reply"

            draft = response.get("content", "")

            # Post-process to improve quality
            improved_draft = self._improve_draft(draft)

            word_count = len(improved_draft.split())
            self.add_reasoning(
                f"✓ Draft reply completed ({word_count} words)", "success"
            )

            return improved_draft

        except Exception as e:
            self.add_reasoning(f"❌ Drafting error: {str(e)}", "error")
            return f"Error generating reply: {str(e)}"

    def analyze_email(
        self, email_content: str, email_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main workflow: Analyze email, research entities, draft reply

        Args:
            email_content: Full email text
            email_metadata: Optional metadata (subject, from, date, etc.)

        Returns:
            Complete analysis results for UI display
        """
        start_time = time.time()
        self.reasoning_steps = []  # Reset reasoning log
        self.stats = {  # Reset stats for this analysis
            "total_entities": 0,
            "entities_searched": 0,
            "entities_known": 0,
            "linkup_sources": 0,
        }

        self.add_reasoning("🚀 Starting email intelligence analysis...")

        # Step 1: Extract entities
        entities = self.extract_entities(email_content)

        # Step 2: Research entities with smart Linkup usage
        research_data = {}
        if entities:
            research_data = self.research_all_entities(entities, email_content)

        # Step 3: Draft reply
        draft_reply = self.draft_reply(email_content, research_data)

        # Collect all sources for display
        all_sources = []
        for entity_research in research_data.values():
            all_sources.extend(entity_research.get("sources", []))

        execution_time = round(time.time() - start_time, 2)
        self.add_reasoning(f"✅ Analysis complete in {execution_time}s", "success")

        # Calculate efficiency metrics
        efficiency_pct = 0
        if self.stats["total_entities"] > 0:
            efficiency_pct = round(
                (self.stats["entities_known"] / self.stats["total_entities"]) * 100, 1
            )

        self.add_reasoning(
            f"📊 Linkup Efficiency: {self.stats['entities_known']}/{self.stats['total_entities']} entities "
            f"({efficiency_pct}%) used existing knowledge, avoided {efficiency_pct}% of API calls",
            "info",
        )

        return {
            "entities": entities,
            "research": research_data,
            "draft_reply": draft_reply,
            "reasoning_steps": self.reasoning_steps,
            "sources": all_sources[:10],  # Limit to top 10
            "execution_time": execution_time,
            "metadata": email_metadata or {},
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stats": {
                "total_entities": self.stats["total_entities"],
                "entities_searched": self.stats["entities_searched"],
                "entities_known": self.stats["entities_known"],
                "linkup_sources": self.stats["linkup_sources"],
                "efficiency_pct": efficiency_pct,
            },
        }
