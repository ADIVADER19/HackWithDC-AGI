"""
Memory Store - Unified memory system for past interactions
Scenario 3: Meeting Preparation

PRIORITY:
1. Fetch from Google APIs (Gmail, Google Calendar) if configured
2. Fall back to JSON cache files (emails, conversations)
Schema-tolerant: searches across all string fields for keyword matching.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class MemoryStore:
    def __init__(self, data_dir=None, gmail_client=None, calendar_client=None):
        """
        Initialize memory store with paths to JSON data files and optional Google API clients.
        
        Args:
            data_dir: Root data directory. Defaults to <project>/data/
            gmail_client: Optional GmailClient instance for fetching real emails
            calendar_client: Optional CalendarClient instance for fetching real events
        """
        if data_dir is None:
            # Walk up from src/memory/ to project root, then into data/
            data_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', '..', 'data'
            )
        self.data_dir = os.path.abspath(data_dir)
        self.emails_path = os.path.join(self.data_dir, 'emails', 'cache.json')
        self.conversations_path = os.path.join(self.data_dir, 'conversations', 'history.json')
        
        # Optional Google API clients
        self.gmail_client = gmail_client
        self.calendar_client = calendar_client

    # ── Read helpers ──────────────────────────────────────────────

    def _load_json(self, filepath: str) -> list:
        """Safely load a JSON file, returning empty list on failure."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            return []
        except (json.JSONDecodeError, IOError) as e:
            print(f"[MemoryStore] Error reading {filepath}: {e}")
            return []

    def _save_json(self, filepath: str, data: list):
        """Safely write data to a JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── Schema-tolerant search ────────────────────────────────────

    def _matches(self, record: dict, keyword: str) -> bool:
        """
        Check if *any* string field in a record contains the keyword.
        This makes us tolerant of different email schemas from Scenario 1.
        """
        keyword_lower = keyword.lower()
        for value in record.values():
            if isinstance(value, str) and keyword_lower in value.lower():
                return True
        return False

    def _parse_datetime(self, record: dict) -> Optional[datetime]:
        """Parse common date formats from record fields."""
        raw = record.get('date') or record.get('timestamp')
        if not raw:
            return None
        if isinstance(raw, (int, float)):
            try:
                return datetime.fromtimestamp(raw / 1000 if raw > 10**11 else raw)
            except (OSError, ValueError):
                return None
        raw = str(raw).strip()
        if raw.isdigit():
            try:
                val = int(raw)
                return datetime.fromtimestamp(val / 1000 if len(raw) >= 12 else val)
            except (OSError, ValueError):
                return None
        try:
            return datetime.fromisoformat(raw.replace('Z', '+00:00'))
        except ValueError:
            return None

    def _normalize_subject(self, subject: str) -> str:
        """Normalize subject for deduping threads."""
        if not subject:
            return ""
        cleaned = subject.lower()
        cleaned = re.sub(r'^\s*(re|fw|fwd)\s*:\s*', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _extract_email_domain(self, text: str) -> str:
        """Extract domain from an email-like string."""
        if not text:
            return ""
        match = re.search(r'[\w\.-]+@([\w\.-]+\.\w+)', text)
        return match.group(1).lower() if match else ""

    def _recent_score(self, dt: Optional[datetime]) -> int:
        """Recency weighting for relevance scoring."""
        if not dt:
            return 0
        age = datetime.now(dt.tzinfo) - dt
        if age <= timedelta(days=30):
            return 2
        if age <= timedelta(days=90):
            return 1
        return 0

    def _score_email(self, company: str, email: dict) -> int:
        """Heuristic relevance score for emails."""
        company_lower = company.lower()
        subject = (email.get('subject') or email.get('title') or "").lower()
        body = (email.get('body') or email.get('content') or "").lower()
        from_field = (email.get('from') or email.get('sender') or "").lower()
        to_field = (email.get('to') or "").lower()

        score = 0
        if company_lower in subject:
            score += 3
        if company_lower in body:
            score += 2
        if company_lower in from_field or company_lower in to_field:
            score += 2

        domain = self._extract_email_domain(from_field)
        if company_lower and domain and company_lower in domain:
            score += 3

        if any(bad in from_field for bad in ['noreply', 'no-reply']):
            score -= 2
        if domain in {'slack.com', 'github.com', 'notifications.google.com'} and company_lower not in subject:
            score -= 2

        score += self._recent_score(self._parse_datetime(email))
        return score

    def _score_conversation(self, company: str, conv: dict) -> int:
        """Heuristic relevance score for meetings/conversations."""
        company_lower = company.lower()
        topic = (conv.get('topic') or conv.get('subject') or "").lower()
        notes = (conv.get('notes') or conv.get('summary') or "").lower()
        attendees = " ".join(conv.get('attendees', [])).lower() if isinstance(conv.get('attendees'), list) else ""
        company_field = (conv.get('company') or "").lower()

        score = 0
        if company_lower in topic:
            score += 3
        if company_lower in notes:
            score += 2
        if company_lower in attendees:
            score += 2
        if company_lower and company_lower in company_field:
            score += 3

        score += self._recent_score(self._parse_datetime(conv))
        return score

    def _sort_by_date(self, records: list) -> list:
        return sorted(
            records,
            key=lambda r: self._parse_datetime(r) or datetime.min,
            reverse=True
        )

    def _filter_emails(self, company: str, emails: list) -> list:
        scored = [(self._score_email(company, e), e) for e in emails]
        scored.sort(key=lambda x: x[0], reverse=True)
        filtered = [e for s, e in scored if s >= 2]
        if not filtered and scored:
            filtered = [e for _, e in scored[:3]]
        return self._sort_by_date(filtered)

    def _dedupe_emails(self, emails: list) -> list:
        """Collapse duplicate threads by normalized subject."""
        seen = {}
        for em in self._sort_by_date(emails):
            key = self._normalize_subject(em.get('subject') or em.get('title') or "")
            if not key:
                key = em.get('id') or str(id(em))
            if key not in seen:
                seen[key] = em
        return list(seen.values())

    def _filter_conversations(self, company: str, conversations: list) -> list:
        scored = [(self._score_conversation(company, c), c) for c in conversations]
        scored.sort(key=lambda x: x[0], reverse=True)
        filtered = [c for s, c in scored if s >= 2]
        if not filtered and scored:
            filtered = [c for _, c in scored[:3]]
        return self._sort_by_date(filtered)

    # ── Public API ────────────────────────────────────────────────

    def search_emails(self, company: str) -> list:
        """
        Search past emails for any mention of a company name.
        PRIORITY:
        1. Fetch from Gmail API if gmail_client available
        2. Fall back to local cache.json file
        
        Args:
            company: Company name to search for (fuzzy keyword match)
        
        Returns:
            List of matching email records, sorted by date (newest first)
        """
        emails = []
        
        # Try Gmail API first
        if self.gmail_client:
            try:
                print(f"[MemoryStore] Fetching emails for {company} from Gmail API...")
                emails = self.gmail_client.search_emails_by_company(company, max_results=15)
                if emails:
                    print(f"[MemoryStore] Found {len(emails)} emails from Gmail for {company}")
                    emails = self._filter_emails(company, emails)
                    emails = self._dedupe_emails(emails)
                    return emails
            except Exception as e:
                print(f"[MemoryStore] Gmail fetch failed: {e}. Falling back to cache.")
        
        # Fall back to local cache
        cached_emails = self._load_json(self.emails_path)
        matches = [e for e in cached_emails if self._matches(e, company)]
        matches = self._filter_emails(company, matches)
        matches = self._dedupe_emails(matches)
        return matches

    def search_conversations(self, company: str) -> list:
        """
        Search past conversations/meeting notes for a company.
        PRIORITY:
        1. Fetch from Google Calendar API if calendar_client available
        2. Fall back to local history.json file
        
        Args:
            company: Company name to search for
        
        Returns:
            List of matching conversation records, newest first
        """
        conversations = []
        
        # Try Google Calendar API first
        if self.calendar_client:
            try:
                print(f"[MemoryStore] Fetching meetings for {company} from Google Calendar...")
                # Fetch both past and upcoming events
                past_events = self.calendar_client.fetch_past_events(days_back=90, max_results=10)
                upcoming_events = self.calendar_client.fetch_events_for_company(company, max_results=10)
                conversations = past_events + upcoming_events
                
                if conversations:
                    print(f"[MemoryStore] Found {len(conversations)} meetings from Calendar for {company}")
                    conversations = self._filter_conversations(company, conversations)
                    return conversations
            except Exception as e:
                print(f"[MemoryStore] Calendar fetch failed: {e}. Falling back to cache.")
        
        # Fall back to local cache
        cached_conversations = self._load_json(self.conversations_path)
        matches = [c for c in cached_conversations if self._matches(c, company)]
        matches = self._filter_conversations(company, matches)
        return matches

    def _summarize_context(self, company: str, emails: list, conversations: list) -> str:
        """Build a concise, relevance-weighted summary for the LLM."""
        summary_parts = []

        # Extract key contacts (clean names only, no emails)
        if emails:
            names = []
            for em in emails:
                sender = em.get('from') or em.get('sender') or ""
                if sender and all(bad not in sender.lower() for bad in ['noreply', 'no-reply', 'notifications']):
                    # Try to extract just the name portion
                    name = re.sub(r'<[^>]+>', '', sender).strip().strip('"\'')
                    if name and '@' not in name:
                        names.append(name)
                    elif '@' in sender:
                        names.append(sender.split('<')[0].strip().strip('"\'') or sender)
            key_contacts = list(dict.fromkeys(names))[:3]
            if key_contacts:
                summary_parts.append(f"Key contacts: {', '.join(key_contacts)}")

        # Email thread subjects (cleaned)
        if emails:
            subjects = []
            for em in emails[:3]:
                subj = em.get('subject') or em.get('title') or ""
                subj = re.sub(r'^\s*(re|fw|fwd)\s*:\s*', '', subj, flags=re.IGNORECASE).strip()
                if subj and subj not in subjects:
                    subjects.append(subj)
            sender_name = key_contacts[0] if key_contacts else "the contact"
            if subjects:
                summary_parts.append(
                    f"Recent email threads with {sender_name} cover: {', '.join(subjects)}."
                )
                # Include body preview for context
                for em in emails[:2]:
                    body = (em.get('body') or em.get('content') or '').strip()[:200]
                    if body:
                        summary_parts.append(f"Email excerpt: {body}")
        else:
            summary_parts.append("No relevant emails found for this company.")

        # Meeting topics (cleaned)
        if conversations:
            topics = []
            for conv in conversations[:3]:
                topic = conv.get('topic') or conv.get('subject') or ""
                topic = re.sub(r'^\s*(re|fw|fwd)\s*:\s*', '', topic, flags=re.IGNORECASE).strip()
                if topic and topic not in topics:
                    topics.append(topic)
            if topics:
                summary_parts.append(
                    f"Recent meetings include: {', '.join(topics)}."
                )
        else:
            summary_parts.append("No relevant meetings found for this company.")

        return "\n".join(summary_parts)

    def get_company_context(self, company: str) -> dict:
        """
        Get all past interactions for a company — the main method used
        by MeetingAgent.
        
        Returns:
            {
                'company': str,
                'emails': [...],
                'conversations': [...],
                'total_interactions': int,
                'last_contact': str or None,
                'summary': str   # human-readable summary for the LLM
            }
        """
        emails = self.search_emails(company)
        conversations = self.search_conversations(company)

        # Find most recent contact date
        all_dates = []
        for record in emails + conversations:
            d = record.get('date', record.get('timestamp'))
            if d:
                all_dates.append(d)
        all_dates.sort(reverse=True)
        last_contact = all_dates[0] if all_dates else None

        summary = self._summarize_context(company, emails, conversations)

        return {
            'company': company,
            'emails': emails,
            'conversations': conversations,
            'total_interactions': len(emails) + len(conversations),
            'last_contact': last_contact,
            'summary': summary
        }

    def save_meeting_interaction(self, company: str, topic: str, notes: str, briefing: str = ""):
        """
        Save a new meeting interaction to conversation history.
        Called after a briefing is generated so future lookups find it.
        """
        conversations = self._load_json(self.conversations_path)
        conversations.append({
            'id': f"meeting_{len(conversations) + 1:03d}",
            'company': company,
            'topic': topic,
            'notes': notes,
            'briefing_generated': briefing[:500] if briefing else "",
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat()
        })
        self._save_json(self.conversations_path, conversations)


# Quick test
if __name__ == "__main__":
    store = MemoryStore()
    context = store.get_company_context("TechCorp")
    print(f"Company: {context['company']}")
    print(f"Total interactions: {context['total_interactions']}")
    print(f"Last contact: {context['last_contact']}")
    print(f"\n--- Summary ---\n{context['summary']}")
