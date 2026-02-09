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
from datetime import datetime
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
                    return emails
            except Exception as e:
                print(f"[MemoryStore] Gmail fetch failed: {e}. Falling back to cache.")
        
        # Fall back to local cache
        cached_emails = self._load_json(self.emails_path)
        matches = [e for e in cached_emails if self._matches(e, company)]
        
        # Sort by date if available (tolerant of missing field)
        matches.sort(
            key=lambda e: e.get('date', e.get('timestamp', '0')),
            reverse=True
        )
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
                    conversations.sort(
                        key=lambda c: c.get('date', c.get('timestamp', '0')),
                        reverse=True
                    )
                    return conversations
            except Exception as e:
                print(f"[MemoryStore] Calendar fetch failed: {e}. Falling back to cache.")
        
        # Fall back to local cache
        cached_conversations = self._load_json(self.conversations_path)
        matches = [c for c in cached_conversations if self._matches(c, company)]
        matches.sort(
            key=lambda c: c.get('date', c.get('timestamp', '0')),
            reverse=True
        )
        return matches

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

        # Build a text summary the LLM can consume
        summary_parts = []
        if emails:
            summary_parts.append(f"Found {len(emails)} past email(s):")
            for em in emails[:5]:  # Limit to 5 most recent
                subj = em.get('subject', em.get('title', 'No subject'))
                date = em.get('date', 'unknown date')
                sender = em.get('from', em.get('sender', 'unknown'))
                body_preview = (em.get('body', em.get('content', '')))[:150]
                summary_parts.append(
                    f"  - [{date}] From: {sender} | Subject: {subj}\n"
                    f"    Preview: {body_preview}"
                )
        else:
            summary_parts.append("No past emails found for this company.")

        if conversations:
            summary_parts.append(f"\nFound {len(conversations)} past meeting(s)/conversation(s):")
            for conv in conversations[:5]:
                topic = conv.get('topic', conv.get('subject', 'No topic'))
                date = conv.get('date', 'unknown date')
                notes = (conv.get('notes', conv.get('summary', '')))[:150]
                summary_parts.append(
                    f"  - [{date}] Topic: {topic}\n"
                    f"    Notes: {notes}"
                )
        else:
            summary_parts.append("\nNo past meetings/conversations found for this company.")

        return {
            'company': company,
            'emails': emails,
            'conversations': conversations,
            'total_interactions': len(emails) + len(conversations),
            'last_contact': last_contact,
            'summary': '\n'.join(summary_parts)
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
