"""
Google OAuth 2.0 Authentication Handler
Manages token refresh, credential caching, and secure session handling for Gmail and Calendar APIs.
"""

import os
import json
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError


class GoogleAuthHandler:
    """
    Handles Google OAuth 2.0 authentication for Gmail and Google Calendar APIs.
    Caches tokens locally and automatically refreshes expired credentials.
    """

    def __init__(self, credentials_file: str = None, token_cache_dir: str = None):
        """
        Initialize OAuth handler.
        
        Args:
            credentials_file: Path to Google OAuth credentials JSON
                             Defaults to config/google_credentials.json
            token_cache_dir: Directory to cache tokens
                           Defaults to data/.google_tokens
        """
        if credentials_file is None:
            credentials_file = os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'config', 'google_credentials.json'
            )
        if token_cache_dir is None:
            token_cache_dir = os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'data', '.google_tokens'
            )

        self.credentials_file = os.path.abspath(credentials_file)
        self.token_cache_dir = os.path.abspath(token_cache_dir)
        os.makedirs(self.token_cache_dir, exist_ok=True)

        # OAuth scopes for Gmail and Calendar
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
            'https://www.googleapis.com/auth/calendar.readonly'  # Read calendar
        ]

        self.credentials = None

    def _get_token_cache_path(self) -> str:
        """Return path to cached token pickle file."""
        return os.path.join(self.token_cache_dir, 'google_token.pickle')

    def authenticate(self) -> Credentials:
        """
        Authenticate user and get valid Google credentials.
        
        Returns:
            google.oauth2.credentials.Credentials object
            
        Raises:
            FileNotFoundError: If google_credentials.json not found
            RefreshError: If token refresh fails
        """
        creds = None
        token_cache = self._get_token_cache_path()

        # Load cached token if exists and valid
        if os.path.exists(token_cache):
            try:
                with open(token_cache, 'rb') as token_file:
                    creds = pickle.load(token_file)
                    print("[GoogleAuth] Loaded cached credentials")
            except (pickle.PickleError, IOError) as e:
                print(f"[GoogleAuth] Failed to load cached token: {e}")
                creds = None

        # Refresh if expired or invalid
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("[GoogleAuth] Refreshed expired credentials")
            except RefreshError as e:
                print(f"[GoogleAuth] Token refresh failed: {e}. Starting new auth flow.")
                creds = None

        # If no valid creds, start OAuth flow
        if not creds or not creds.valid:
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(
                    f"Google credentials not found at {self.credentials_file}\n"
                    "Download OAuth 2.0 credentials from Google Cloud Console "
                    "(Desktop app) and save as google_credentials.json"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES
            )
            creds = flow.run_local_server(port=0)
            print("[GoogleAuth] Completed interactive auth flow")

        # Cache token for future use
        with open(token_cache, 'wb') as token_file:
            pickle.dump(creds, token_file)
            print(f"[GoogleAuth] Cached credentials to {token_cache}")

        self.credentials = creds
        return creds

    def get_credentials(self, force_refresh: bool = False) -> Credentials:
        """
        Get valid Google credentials (cached if available).
        
        Args:
            force_refresh: Force re-authentication even if cached creds exist
            
        Returns:
            google.oauth2.credentials.Credentials object
        """
        if force_refresh or self.credentials is None:
            self.authenticate()
        return self.credentials

    def revoke_token(self):
        """Revoke cached token and force re-authentication on next call."""
        token_cache = self._get_token_cache_path()
        if os.path.exists(token_cache):
            os.remove(token_cache)
            self.credentials = None
            print("[GoogleAuth] Revoked cached token")
