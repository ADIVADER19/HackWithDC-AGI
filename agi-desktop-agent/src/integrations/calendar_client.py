"""
Google Calendar API Client - Fetch and standardize calendar events.
Maps Google Calendar event format to local history.json schema (meetings/conversations).
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dateutil import parser as dateutil_parser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .google_auth import GoogleAuthHandler


class CalendarClient:
    """
    Client for reading calendar events from Google Calendar API.
    Converts calendar events to meeting/conversation schema for compatibility.
    """

    def __init__(self, google_auth: GoogleAuthHandler):
        """
        Initialize Calendar client.
        
        Args:
            google_auth: GoogleAuthHandler instance with valid credentials
        """
        self.auth = google_auth
        self.service = None
        self._init_service()

    def _init_service(self):
        """Initialize Google Calendar API service."""
        try:
            creds = self.auth.get_credentials()
            self.service = build('calendar', 'v3', credentials=creds)
            print("[CalendarClient] Google Calendar API service initialized")
        except Exception as e:
            print(f"[CalendarClient] Failed to initialize Calendar service: {e}")
            self.service = None

    def _parse_datetime(self, dt_str: str) -> str:
        """
        Parse ISO datetime string to YYYY-MM-DD format.
        Handles both datetime and date formats.
        
        Args:
            dt_str: ISO datetime or date string
            
        Returns:
            YYYY-MM-DD formatted date
        """
        try:
            if isinstance(dt_str, dict):  # {'date': '2025-12-10'} format
                return dt_str['date']
            dt = dateutil_parser.isoparse(dt_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            return datetime.now().strftime('%Y-%m-%d')

    def _extract_company_from_event(self, event: dict) -> str:
        """
        Infer company name from event title or attendees.
        
        Args:
            event: Calendar event object
            
        Returns:
            Company name or 'Unknown'
        """
        title = event.get('summary', '').lower()
        description = event.get('description', '').lower()

        # Check common company keywords
        keywords = {
            'techcorp': 'TechCorp',
            'innovatech': 'InnovaTech',
            'globalfinance': 'GlobalFinance',
            'google': 'Google',
            'microsoft': 'Microsoft',
            'amazon': 'Amazon',
            'intel': 'Intel',
        }

        text_to_search = title + ' ' + description
        for keyword, company_name in keywords.items():
            if keyword in text_to_search:
                return company_name

        # Try to extract from attendees
        attendees = event.get('attendees', [])
        for attendee in attendees:
            email = attendee.get('email', '').lower()
            for keyword, company_name in keywords.items():
                if keyword in email:
                    return company_name

        return "Unknown"

    def _extract_attendees(self, event: dict) -> List[str]:
        """
        Extract attendee names from calendar event.
        
        Args:
            event: Calendar event object
            
        Returns:
            List of attendee names (display name or email)
        """
        attendees = []
        for attendee in event.get('attendees', []):
            name = attendee.get('displayName') or attendee.get('email', '')
            if name:
                attendees.append(name)
        return attendees

    def _standardize_event(self, event: dict, event_id: str) -> Dict:
        """
        Convert Google Calendar event to meeting schema.
        
        Args:
            event: Calendar event object from API
            event_id: Unique event ID
            
        Returns:
            Standardized meeting dict matching history.json schema
        """
        start_time = event.get('start', {})
        start_date = self._parse_datetime(
            start_time.get('dateTime') or start_time.get('date', '')
        )

        summary = event.get('summary', 'Untitled Meeting')
        description = event.get('description', '')
        attendees = self._extract_attendees(event)

        return {
            'id': f"meeting_cal_{event_id[:20]}",
            'company': self._extract_company_from_event(event),
            'topic': summary,
            'date': start_date,
            'timestamp': event.get('created', datetime.now().isoformat()),
            'attendees': attendees,
            'notes': description[:500] if description else summary,
            'outcome': 'Scheduled - awaiting completion',
            'next_steps': f"Prepare for meeting: {summary}",
            'source': 'google_calendar'
        }

    def fetch_events(
        self,
        days_ahead: int = 30,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Fetch upcoming calendar events.
        
        Args:
            days_ahead: How many days into future to fetch (default 30)
            max_results: Maximum events to return (default 20)
            
        Returns:
            List of standardized meeting dicts
        """
        if not self.service:
            print("[CalendarClient] Calendar service not initialized, returning empty list")
            return []

        events = []
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'

            results = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            items = results.get('items', [])
            if not items:
                print(f"[CalendarClient] No events found in next {days_ahead} days")
                return []

            for item in items:
                try:
                    standardized = self._standardize_event(item, item.get('id', 'unknown'))
                    events.append(standardized)
                    print(f"[CalendarClient] Fetched event: {standardized['topic']}")
                except Exception as e:
                    print(f"[CalendarClient] Error standardizing event: {e}")

            return events

        except HttpError as e:
            print(f"[CalendarClient] Calendar API error: {e}")
            return []

    def fetch_events_for_company(
        self,
        company: str,
        days_ahead: int = 30,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Fetch upcoming events mentioning a specific company.
        
        Args:
            company: Company name to search for
            days_ahead: Days to look ahead
            max_results: Max events to return
            
        Returns:
            List of standardized meeting dicts for that company
        """
        all_events = self.fetch_events(days_ahead, max_results * 2)
        
        # Filter for company
        company_lower = company.lower()
        filtered = [
            e for e in all_events
            if company_lower in e.get('topic', '').lower()
            or company_lower in e.get('notes', '').lower()
            or any(company_lower in att.lower() for att in e.get('attendees', []))
        ]

        return filtered[:max_results]

    def fetch_past_events(
        self,
        days_back: int = 90,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Fetch past calendar events (completed meetings).
        
        Args:
            days_back: How many days back to search (default 90)
            max_results: Max events to return
            
        Returns:
            List of standardized meeting dicts
        """
        if not self.service:
            print("[CalendarClient] Calendar service not initialized, returning empty list")
            return []

        events = []
        try:
            time_min = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + 'Z'
            now = datetime.utcnow().isoformat() + 'Z'

            results = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            items = results.get('items', [])
            for item in items:
                standardized = self._standardize_event(item, item.get('id', 'unknown'))
                standardized['outcome'] = 'Completed'
                events.append(standardized)

            return sorted(events, key=lambda e: e.get('date', ''), reverse=True)

        except HttpError as e:
            print(f"[CalendarClient] Calendar API error: {e}")
            return []
