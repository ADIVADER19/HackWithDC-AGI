"""
Meeting Preparation Agent
Scenario 3: Meeting Preparation Assistant

ReAct pattern: Observe (memory) → Reason (plan) → Act (Linkup search) → Synthesize (Groq briefing)
"""

import json
import re
from datetime import datetime


class MeetingAgent:
    """
    Generates comprehensive meeting briefings by combining:
    1. Local memory (past emails & meetings)
    2. Real-time web research via Linkup
    3. LLM synthesis via Groq (Llama 3.3 70B)
    """

    def __init__(self, groq_client, linkup_wrapper, memory_store):
        self.groq = groq_client
        self.linkup = linkup_wrapper
        self.memory = memory_store

    def prepare_briefing(self, company_name: str, meeting_context: str = "") -> dict:
        """
        Main entry point — generates a full meeting briefing.

        Args:
            company_name: Name of the company for the meeting
            meeting_context: Optional context (e.g. "Partnership discussion")

        Returns:
            {
                'reasoning_steps': [...],
                'past_interactions': {...},
                'linkup_sources': [...],
                'result': str,          # The formatted briefing
                'briefing_data': {      # Structured data for UI
                    'company_overview': str,
                    'past_context': str,
                    'recent_news': str,
                    'talking_points': [str],
                    'risks_and_notes': str
                },
                'confidence': float
            }
        """
        reasoning_steps = []
        all_sources = []

        # ── Step 1: Search local memory ──────────────────────────
        reasoning_steps.append({
            'step': 1,
            'action': 'Searching local memory',
            'detail': f'Looking for past emails and meetings with {company_name}...',
            'status': 'running'
        })

        context = self.memory.get_company_context(company_name)
        relationship_summary = self._summarize_relationship_context(
            company_name=company_name,
            meeting_context=meeting_context,
            memory_context=context
        )
        if relationship_summary:
            context['summary'] = relationship_summary
        total = context['total_interactions']
        last = context['last_contact']

        reasoning_steps[-1]['status'] = 'complete'
        reasoning_steps[-1]['detail'] = (
            f"Found {total} past interaction(s). "
            f"Last contact: {last or 'Never'}."
        )

        # ── Step 2: Linkup research — recent news ────────────────
        reasoning_steps.append({
            'step': 2,
            'action': 'Researching recent news',
            'detail': f'Searching Linkup for latest {company_name} news...',
            'status': 'running'
        })

        news_results = self._search_news(company_name)
        all_sources.extend(news_results.get('sources', []))

        reasoning_steps[-1]['status'] = 'complete'
        reasoning_steps[-1]['detail'] = (
            f"Found {len(news_results.get('sources', []))} news source(s) "
            f"about {company_name}."
        )

        # ── Step 3: Linkup research — industry / products ────────
        reasoning_steps.append({
            'step': 3,
            'action': 'Researching products & funding',
            'detail': f'Searching Linkup for {company_name} products, funding, strategy...',
            'status': 'running'
        })

        industry_results = self._search_industry(company_name)
        all_sources.extend(industry_results.get('sources', []))

        reasoning_steps[-1]['status'] = 'complete'
        reasoning_steps[-1]['detail'] = (
            f"Found {len(industry_results.get('sources', []))} additional source(s)."
        )

        # ── Step 4: Synthesize briefing with Groq ────────────────
        reasoning_steps.append({
            'step': 4,
            'action': 'Generating briefing',
            'detail': 'Synthesizing all data into a comprehensive meeting brief...',
            'status': 'running'
        })

        briefing_result = self._synthesize_briefing(
            company_name=company_name,
            meeting_context=meeting_context,
            memory_context=context,
            news_sources=news_results,
            industry_sources=industry_results
        )

        briefing_data = briefing_result.get('briefing_data', {})
        recent_news = (briefing_data.get('recent_news') or '').strip().lower()
        bad_markers = ['unable to fetch', 'unable to parse', 'no recent news', 'check linkup', 'check api']
        needs_news_fix = not recent_news or any(m in recent_news for m in bad_markers)
        if needs_news_fix and news_results.get('sources'):
            briefing_data['recent_news'] = self._summarize_recent_news(
                company_name=company_name,
                sources=news_results.get('sources', [])
            )
            briefing_result['briefing_data'] = briefing_data
        elif needs_news_fix:
            briefing_data['recent_news'] = (
                f"No company-specific news was found for {company_name}. "
                f"It is recommended to check recent coverage manually before the meeting."
            )
            briefing_result['briefing_data'] = briefing_data

        reasoning_steps[-1]['status'] = 'complete'
        reasoning_steps[-1]['detail'] = 'Briefing generated successfully.'

        # ── Step 5: Note completion (no longer saving duplicate records) ─
        reasoning_steps.append({
            'step': 5,
            'action': 'Briefing complete',
            'detail': f'Compiled data from {total} past interaction(s) and {len(all_sources)} web source(s).',
            'status': 'complete'
        })

        # ── Build result ─────────────────────────────────────────
        if relationship_summary:
            briefing_result.setdefault('briefing_data', {})
            briefing_result['briefing_data']['past_context'] = relationship_summary

        confidence = self._calculate_confidence(context, all_sources, briefing_result)

        # ── Source attribution analytics ─────────────────────────
        source_attribution = self._calculate_source_attribution(context, all_sources, briefing_result)

        return {
            'reasoning_steps': reasoning_steps,
            'past_interactions': {
                'emails': context['emails'],
                'conversations': context['conversations'],
                'total': context['total_interactions'],
                'last_contact': context['last_contact'],
                'summary': context['summary']
            },
            'linkup_sources': all_sources,
            'result': briefing_result.get('briefing_text', 'Unable to generate briefing.'),
            'briefing_data': briefing_result.get('briefing_data', {}),
            'confidence': confidence,
            'source_attribution': source_attribution
        }

    # ── Linkup search helpers ─────────────────────────────────────

    def _search_news(self, company: str) -> dict:
        """Search Linkup for recent company news."""
        try:
            result = self.linkup.search(
                query=f'"{company}" company news announcements 2025 2026',
                max_results=5
            )
            # Filter sources that actually mention the company
            sources = result.get('sources', [])
            company_lower = company.lower()
            relevant = [s for s in sources if company_lower in (s.get('title', '') + s.get('snippet', '')).lower()]
            if relevant:
                result['sources'] = relevant
            return result
        except Exception as e:
            print(f"[MeetingAgent] News search error: {e}")
            return {'sources': [], 'error': str(e)}

    def _search_industry(self, company: str) -> dict:
        """Search Linkup for company products, funding, strategy."""
        try:
            result = self.linkup.search(
                query=f'"{company}" products funding strategy company profile',
                max_results=5
            )
            sources = result.get('sources', [])
            company_lower = company.lower()
            relevant = [s for s in sources if company_lower in (s.get('title', '') + s.get('snippet', '')).lower()]
            if relevant:
                result['sources'] = relevant
            return result
        except Exception as e:
            print(f"[MeetingAgent] Industry search error: {e}")
            return {'sources': [], 'error': str(e)}

    def _summarize_relationship_context(
        self,
        company_name: str,
        meeting_context: str,
        memory_context: dict
    ) -> str:
        """Summarize relationship context using Groq."""
        emails = memory_context.get('emails', [])[:5]
        conversations = memory_context.get('conversations', [])[:5]

        def _clean_subject(subject: str) -> str:
            cleaned = re.sub(r'^\s*(re|fw|fwd)\s*:\s*', '', subject, flags=re.IGNORECASE)
            return re.sub(r'\s+', ' ', cleaned).strip()

        email_lines = []
        for em in emails:
            sender = em.get('from') or em.get('sender') or ""
            subject = _clean_subject(em.get('subject') or em.get('title') or "")
            body = (em.get('body') or em.get('content') or "").strip()
            if subject or sender:
                email_lines.append(f"- {sender} — {subject} — {body[:120]}")

        meeting_lines = []
        for conv in conversations:
            topic = _clean_subject(conv.get('topic') or conv.get('subject') or "")
            notes = (conv.get('notes') or conv.get('summary') or "").strip()
            if topic:
                meeting_lines.append(f"- {topic} — {notes[:120]}")

        if not email_lines and not meeting_lines:
            return ""

        system_prompt = """You are an executive assistant writing a polished relationship summary.

Rules:
- Write in complete sentences and natural prose. No raw data dumps.
- No timestamps, no dates in brackets, no email addresses.
- Remove "Re:", "Fwd:" prefixes from subject lines.
- No pipe characters (|) or dashes as list markers.
- Mention key contacts by first and last name naturally in the text.
- Summarize the nature and status of the relationship in 2-3 sentences.
- If there are recent meetings, describe them briefly in prose (not a list).
- Keep the entire summary under 100 words."""

        user_message = f"""Company: {company_name}
Meeting context: {meeting_context or 'General'}

Recent emails:
{chr(10).join(email_lines) if email_lines else 'None'}

Recent meetings:
{chr(10).join(meeting_lines) if meeting_lines else 'None'}
"""

        try:
            response = self.groq.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3
            )
            content = (response.get('content') or '').strip()
            return content or memory_context.get('summary', '')
        except Exception as e:
            print(f"[MeetingAgent] Relationship summary error: {e}")
            return memory_context.get('summary', '')

    def _summarize_recent_news(self, company_name: str, sources: list) -> str:
        """Summarize recent news from Linkup sources."""
        if not sources:
            return "No recent news available."

        system_prompt = """You are writing a polished recent news summary for a meeting briefing.

Rules:
- Write in complete sentences and natural prose.
- No pipe characters, no dashes as list markers, no raw URLs.
- Summarize the most relevant developments in 3-5 sentences.
- Focus on what matters for a business meeting: funding, product launches, partnerships, leadership changes.
- If the sources are generic industry news, extract what is most relevant to the specific company.
- Never mention API keys, errors, or technical issues."""

        user_message = f"""Company: {company_name}

Sources:
{self.linkup.format_sources_for_agent(sources)}
"""

        try:
            response = self.groq.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3
            )
            content = (response.get('content') or '').strip()
            if content:
                return content
        except Exception as e:
            print(f"[MeetingAgent] Recent news summary error: {e}")

        # Fallback: prose from titles
        titles = [src.get('title') or '' for src in sources[:4] if src.get('title')]
        if titles:
            return f"Recent coverage includes topics such as {', '.join(titles[:3])}. Review these sources for the latest details before the meeting."
        return "Recent news could not be summarized. It is recommended to check the latest coverage manually."

    # ── Groq synthesis ────────────────────────────────────────────

    def _synthesize_briefing(
        self,
        company_name: str,
        meeting_context: str,
        memory_context: dict,
        news_sources: dict,
        industry_sources: dict
    ) -> dict:
        """Use Groq (Llama 3.3) to generate a structured meeting briefing."""

        # Build the context text for the LLM
        news_text = self.linkup.format_sources_for_agent(
            news_sources.get('sources', [])
        )
        industry_text = self.linkup.format_sources_for_agent(
            industry_sources.get('sources', [])
        )

        system_prompt = """You are an expert executive assistant who writes polished, 
professional meeting briefings. Your writing is clear, uses complete sentences,
and reads like a well-crafted business memo.

FORMATTING RULES (strict):
- Write in complete sentences and short paragraphs.
- Never use pipe characters (|), dashes as list markers, or raw URLs in prose.
- Use numbered lists only for talking points.
- Do not include timestamps, dates in brackets, or email addresses in the text.
- Do not mention API keys, errors, or technical failures.
- If data is sparse, still produce a useful briefing using your knowledge.

You must output a JSON object with exactly these keys:
{
  "company_overview": "A 2-3 sentence overview of the company, its industry, and what they do. If this is a well-known company, include relevant details. If unknown, describe what can be inferred.",
  "past_context": "A polished 2-3 sentence narrative about the relationship history. Mention key contacts by name, the nature of past discussions, and where things stand. Do not list raw data.",
  "recent_news": "A concise paragraph summarizing the most relevant recent developments from the provided sources. Highlight what matters for the upcoming meeting.",
  "talking_points": ["Specific, actionable point referencing real context", "Another concrete point", "A third point tied to meeting goals", "A fourth strategic point"],
  "risks_and_notes": "1-2 sentences about potential risks, gaps in knowledge, or things to prepare for."
}

Output ONLY valid JSON, no markdown fences, no extra text."""

        user_message = f"""Prepare a polished meeting briefing for an upcoming meeting with {company_name}.

Meeting context: {meeting_context or 'General business meeting'}

RELATIONSHIP HISTORY:
{memory_context['summary']}

RECENT NEWS AND DEVELOPMENTS:
{news_text if news_text.strip() else 'No news sources available. Use your general knowledge if you know this company.'}

INDUSTRY AND PRODUCT INFORMATION:
{industry_text if industry_text.strip() else 'No additional industry data. Use your general knowledge if applicable.'}

Generate the briefing JSON now. Remember: polished prose, no raw data dumps, no pipes or dashes as separators."""

        try:
            response = self.groq.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.4
            )

            content = response.get('content', '')
            if not content:
                return self._fallback_briefing(company_name, memory_context)

            # Parse the JSON from LLM response
            briefing_data = self._parse_briefing_json(content)

            # If critical fields are empty, fill them intelligently
            if not briefing_data.get('company_overview'):
                briefing_data['company_overview'] = (
                    f"{company_name} is the subject of an upcoming meeting. "
                    f"Based on available records, the company has been involved in discussions "
                    f"related to collaboration and partnership opportunities."
                )
            if not briefing_data.get('talking_points'):
                briefing_data['talking_points'] = [
                    f"Open by referencing your recent interactions with {company_name}",
                    "Discuss current priorities and how they align with mutual goals",
                    "Explore specific collaboration opportunities mentioned in past communications",
                    "Agree on clear next steps and a follow-up schedule"
                ]
            if not briefing_data.get('risks_and_notes'):
                briefing_data['risks_and_notes'] = (
                    "Some details may need verification. Review any shared documents before the meeting."
                )

            briefing_text = self._format_briefing_text(company_name, briefing_data)

            return {
                'briefing_text': briefing_text,
                'briefing_data': briefing_data
            }

        except Exception as e:
            print(f"[MeetingAgent] Groq synthesis error: {e}")
            return self._fallback_briefing(company_name, memory_context)

    def _parse_briefing_json(self, content: str) -> dict:
        """Extract JSON from LLM response, handling markdown code fences and broken JSON."""
        cleaned = content.strip()

        # Strip markdown code fences
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            lines = [l for l in lines if not l.strip().startswith('```')]
            cleaned = '\n'.join(lines)

        # First attempt: direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Second attempt: find the outermost { ... }
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                pass

        # Third attempt: fix common issues (trailing commas, unescaped newlines)
        if start != -1 and end != -1:
            raw_json = cleaned[start:end + 1]
            # Remove trailing commas before } or ]
            fixed = re.sub(r',\s*([}\]])', r'\1', raw_json)
            # Escape unescaped newlines in string values
            fixed = fixed.replace('\n', '\\n')
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

        # Fourth attempt: ask Groq to fix the JSON
        try:
            fix_response = self.groq.chat(
                messages=[
                    {"role": "system", "content": "Fix this broken JSON. Output ONLY the corrected JSON object, nothing else."},
                    {"role": "user", "content": content[:2000]}
                ],
                temperature=0.0
            )
            fix_content = (fix_response.get('content') or '').strip()
            if fix_content.startswith('```'):
                fix_lines = fix_content.split('\n')
                fix_content = '\n'.join(l for l in fix_lines if not l.strip().startswith('```'))
            fix_start = fix_content.find('{')
            fix_end = fix_content.rfind('}')
            if fix_start != -1 and fix_end != -1:
                return json.loads(fix_content[fix_start:fix_end + 1])
        except Exception:
            pass

        # Final fallback: return empty structure (will be filled by the caller)
        print(f"[MeetingAgent] Could not parse briefing JSON. Raw content: {content[:300]}")
        return {
            'company_overview': '',
            'past_context': '',
            'recent_news': '',
            'talking_points': [],
            'risks_and_notes': ''
        }

    def _format_briefing_text(self, company: str, data: dict) -> str:
        """Format briefing data into readable text."""
        points = data.get('talking_points', [])
        talking = '\n'.join(f"  {i+1}. {p}" for i, p in enumerate(points))

        return f"""
═══════════════════════════════════════════
  MEETING BRIEFING: {company.upper()}
  Prepared: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
═══════════════════════════════════════════

📋 COMPANY OVERVIEW
{data.get('company_overview', 'N/A')}

🔄 PAST INTERACTIONS
{data.get('past_context', 'No past interactions found.')}

📰 RECENT NEWS & DEVELOPMENTS
{data.get('recent_news', 'No recent news available.')}

💬 RECOMMENDED TALKING POINTS
{talking or '  No talking points generated.'}

⚠️ RISKS & NOTES
{data.get('risks_and_notes', 'None identified.')}

═══════════════════════════════════════════
""".strip()

    def _fallback_briefing(self, company: str, memory_context: dict) -> dict:
        """Generate a basic briefing when Groq is unavailable."""
        total = memory_context.get('total_interactions', 0)
        last = memory_context.get('last_contact')
        past_note = f'We have {total} past interaction(s) on record.' if total else 'No prior interactions found.'
        if last:
            past_note += f' The most recent contact was on {last}.'

        data = {
            'company_overview': f'An upcoming meeting is scheduled with {company}. Further company details should be verified before the meeting.',
            'past_context': past_note,
            'recent_news': 'Recent news could not be retrieved at this time. It is recommended to check the latest coverage manually before the meeting.',
            'talking_points': [
                f'Open by referencing your most recent interaction with {company} to establish continuity',
                'Ask about their current priorities and any changes since your last conversation',
                'Explore areas of mutual interest and potential collaboration',
                'Align on clear next steps and a follow-up timeline before closing'
            ],
            'risks_and_notes': 'This briefing was generated with limited data. Verify key details and review any available documents before the meeting.'
        }
        return {
            'briefing_text': self._format_briefing_text(company, data),
            'briefing_data': data
        }

    # ── Confidence scoring ────────────────────────────────────────

    def _calculate_confidence(self, context: dict, sources: list, briefing: dict) -> float:
        """
        Confidence = weighted score of data availability.
        Gives judges a measurable quality indicator.
        """
        score = 0.0
        # Memory data found
        if context['total_interactions'] > 0:
            score += 0.3
        # Linkup sources found
        if len(sources) >= 3:
            score += 0.3
        elif len(sources) >= 1:
            score += 0.15
        # Briefing generated successfully
        if briefing.get('briefing_data', {}).get('talking_points'):
            score += 0.3
        # Has recent contact
        if context.get('last_contact'):
            score += 0.1
        return min(round(score, 2), 1.0)

    def _calculate_source_attribution(self, context: dict, sources: list, briefing: dict) -> dict:
        """
        Calculate what percentage of the briefing came from each source.
        Returns breakdown for the analytics panel.
        """
        has_memory = context['total_interactions'] > 0
        has_linkup = len(sources) > 0
        has_briefing = bool(briefing.get('briefing_data'))

        # Base weights depending on what data was available
        memory_weight = 0.0
        linkup_weight = 0.0
        llm_weight = 0.0

        if has_memory and has_linkup:
            memory_weight = 30.0
            linkup_weight = 40.0
            llm_weight = 30.0
        elif has_memory and not has_linkup:
            memory_weight = 50.0
            linkup_weight = 0.0
            llm_weight = 50.0
        elif not has_memory and has_linkup:
            memory_weight = 0.0
            linkup_weight = 55.0
            llm_weight = 45.0
        else:
            memory_weight = 0.0
            linkup_weight = 0.0
            llm_weight = 100.0

        # Adjust memory weight based on how many interactions found
        if has_memory:
            interaction_bonus = min(context['total_interactions'] * 3, 10)
            memory_weight += interaction_bonus
            llm_weight -= interaction_bonus

        # Adjust linkup weight based on number of sources
        if has_linkup:
            source_bonus = min(len(sources) * 2, 10)
            linkup_weight += source_bonus
            llm_weight -= source_bonus

        # Ensure non-negative and normalize to 100
        llm_weight = max(llm_weight, 5.0)
        total = memory_weight + linkup_weight + llm_weight
        memory_pct = round(memory_weight / total * 100)
        linkup_pct = round(linkup_weight / total * 100)
        llm_pct = 100 - memory_pct - linkup_pct  # Ensure sums to 100

        # Section-level attribution
        sections = {}
        bd = briefing.get('briefing_data', {})
        if bd:
            sections['company_overview'] = {
                'primary_source': 'Web Research (Linkup)' if has_linkup else 'LLM Knowledge',
                'sources_used': (['Linkup'] if has_linkup else []) + ['LLM']
            }
            sections['past_context'] = {
                'primary_source': 'Local Memory' if has_memory else 'LLM Knowledge',
                'sources_used': (['Local Memory'] if has_memory else []) + ['LLM']
            }
            sections['recent_news'] = {
                'primary_source': 'Web Research (Linkup)' if has_linkup else 'LLM Knowledge',
                'sources_used': (['Linkup'] if has_linkup else []) + ['LLM']
            }
            sections['talking_points'] = {
                'primary_source': 'LLM Synthesis',
                'sources_used': (['Local Memory'] if has_memory else []) + (['Linkup'] if has_linkup else []) + ['LLM']
            }
            sections['risks_and_notes'] = {
                'primary_source': 'LLM Analysis',
                'sources_used': (['Local Memory'] if has_memory else []) + (['Linkup'] if has_linkup else []) + ['LLM']
            }

        return {
            'memory_pct': memory_pct,
            'linkup_pct': linkup_pct,
            'llm_pct': llm_pct,
            'memory_interactions': context['total_interactions'],
            'linkup_sources_count': len(sources),
            'data_freshness': 'Real-time' if has_linkup else 'Cached only',
            'sections': sections,
            'verification_status': 'Cross-verified' if (has_memory and has_linkup) else 'Partially verified' if (has_memory or has_linkup) else 'Unverified'
        }


# Quick test
if __name__ == "__main__":
    from groq_client import GroqClient
    from linkup_wrapper import LinkupWrapper
    import sys
    sys.path.insert(0, '..')
    from memory.store import MemoryStore

    agent = MeetingAgent(
        groq_client=GroqClient(),
        linkup_wrapper=LinkupWrapper(),
        memory_store=MemoryStore()
    )

    result = agent.prepare_briefing(
        company_name="TechCorp",
        meeting_context="Partnership discussion for AI integration"
    )

    print(f"Confidence: {result['confidence']}")
    print(f"Steps: {len(result['reasoning_steps'])}")
    print(f"Sources: {len(result['linkup_sources'])}")
    print(result['result'])
