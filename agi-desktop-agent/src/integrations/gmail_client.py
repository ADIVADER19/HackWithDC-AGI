"""
Gmail API Client - Fetch and standardize emails from Google Gmail.
Maps Gmail message format to local cache.json schema.
"""

import os
import base64
from datetime import datetime
from email.mime.text import MIMEText
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .google_auth import GoogleAuthHandler


class GmailClient:
    """
    Client for reading emails from Gmail via Google API.
    Converts Gmail message format to standard email schema for compatibility.
    """

    def __init__(self, google_auth: GoogleAuthHandler):
        """
        Initialize Gmail client.
        
        Args:
            google_auth: GoogleAuthHandler instance with valid credentials
        """
        self.auth = google_auth
        self.service = None
        self._init_service()

    def _init_service(self):
        """Initialize Gmail API service."""
        try:
            creds = self.auth.get_credentials()
            self.service = build('gmail', 'v1', credentials=creds)
            print("[GmailClient] Gmail API service initialized")
        except Exception as e:
            print(f"[GmailClient] Failed to initialize Gmail service: {e}")
            self.service = None

    def _decode_message_part(self, part: dict) -> str:
        """
        Safely decode email message part (handles encoding).
        
        Args:
            part: Email part from Gmail API
            
        Returns:
            Decoded string content
        """
        try:
            if 'data' in part:
                data = part['data'].replace('-', '+').replace('_', '/')
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"[GmailClient] Error decoding part: {e}")
        return ""

    def _extract_body(self, message: dict) -> str:
        """
        Extract readable email body from Gmail message.
        
        Args:
            message: Gmail message object
            
        Returns:
            Email body text (plain text or HTML stripped)
        """
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = self._decode_message_part(part)
                    break
            # Fallback to HTML if no plain text
            if not body:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/html':
                        body = self._decode_message_part(part)
                        break
        else:
            # Simple message without parts
            body = self._decode_message_part(message['payload'])
        
        return body.strip()[:1000]  # Limit to 1000 chars

    def _get_header(self, headers: list, name: str) -> str:
        """Extract specific header from Gmail headers list."""
        for header in headers:
            if header['name'] == name:
                return header['value']
        return ""

    def _timestamp_to_date(self, timestamp_ms: str) -> str:
        """Convert Gmail timestamp (ms since epoch) to YYYY-MM-DD format."""
        try:
            timestamp_s = int(timestamp_ms) / 1000
            return datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d')
        except (ValueError, OSError):
            return datetime.now().strftime('%Y-%m-%d')

    def _extract_company_from_email(self, email: str) -> str:
        """
        Extract company name from email domain.
        E.g., sarah.chen@techcorp.com -> "TechCorp"
        
        Args:
            email: Email address
            
        Returns:
            Inferred company name or 'Unknown'
        """
        try:
            domain = email.split('@')[1].split('.')[0]
            return domain.capitalize()
        except (IndexError, AttributeError):
            return "Unknown"

    def _standardize_message(self, message: dict, message_id: str) -> Dict:
        """
        Convert Gmail message to standard email schema.
        
        Args:
            message: Gmail message object from API
            message_id: Unique message ID
            
        Returns:
            Standardized email dict with schema matching cache.json
        """
        headers = message['payload']['headers']
        from_email = self._get_header(headers, 'From')
        to_email = self._get_header(headers, 'To')
        subject = self._get_header(headers, 'Subject')
        timestamp = message.get('internalDate', '0')

        return {
            'id': f"email_gmail_{message_id[:20]}",
            'from': from_email,
            'to': to_email,
            'subject': subject,
            'date': self._timestamp_to_date(timestamp),
            'timestamp': timestamp,
            'body': self._extract_body(message),
            'company': self._extract_company_from_email(from_email),
            'source': 'gmail'
        }

    def fetch_emails(
        self,
        query: str = 'is:inbox',
        max_results: int = 20
    ) -> List[Dict]:
        """
        Fetch emails from Gmail matching a query.
        
        Args:
            query: Gmail search query (see Gmail API docs)
                  'is:inbox' - inbox only (default)
                  'from:user@company.com' - specific sender
                  'subject:partnership' - keyword search
                  'after:2025-01-01' - date filter
            max_results: Maximum emails to fetch (default 20)
            
        Returns:
            List of standardized email dicts
        """
        if not self.service:
            print("[GmailClient] Gmail service not initialized, returning empty list")
            return []

        emails = []
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                print(f"[GmailClient] No emails found for query: {query}")
                return []

            for message_info in messages:
                try:
                    # Fetch full message details
                    message = self.service.users().messages().get(
                        userId='me',
                        id=message_info['id'],
                        format='full'
                    ).execute()

                    standardized = self._standardize_message(message, message_info['id'])
                    emails.append(standardized)
                    print(f"[GmailClient] Fetched email: {standardized['subject']}")

                except HttpError as e:
                    print(f"[GmailClient] Error fetching message {message_info['id']}: {e}")

            return emails

        except HttpError as e:
            print(f"[GmailClient] Gmail API error: {e}")
            return []

    def search_emails_by_company(self, company: str, max_results: int = 10) -> List[Dict]:
        """
        Search Gmail for emails related to a company.
        
        Args:
            company: Company name to search for
            max_results: Max emails to retrieve
            
        Returns:
            List of standardized email dicts
        """
        # Build query: search company name in all fields
        query = f'from:{company.lower()} OR to:{company.lower()} OR subject:{company.lower()}'
        return self.fetch_emails(query, max_results)

    def fetch_unread_emails(self, max_results: int = 10) -> List[Dict]:
        """
        Fetch unread emails from inbox.
        
        Args:
            max_results: Max unread emails to fetch
            
        Returns:
            List of standardized email dicts
        """
        return self.fetch_emails('is:unread is:inbox', max_results)

    def fetch_recent_emails(self, max_results: int = 20) -> List[Dict]:
        """
        Fetch most recent emails from inbox.
        
        Args:
            max_results: Max emails to fetch
            
        Returns:
            List of standardized email dicts (sorted by date, newest first)
        """
        emails = self.fetch_emails('is:inbox', max_results)
        # Sort by date descending (newest first)
        return sorted(emails, key=lambda e: e.get('timestamp', '0'), reverse=True)
