# Google API Integration Setup Guide

This guide walks you through setting up Gmail and Google Calendar integration for the AGI Desktop Intelligence Agent.

## Quick Start

### 1. Prerequisites

Install the required Google API libraries:

```bash
pip install -r requirements.txt
```

This includes:
- `google-auth-oauthlib==1.2.0`
- `google-auth-httplib2==0.2.0`
- `google-api-python-client==2.108.0`
- `python-dateutil==2.8.2`

### 2. Create Google OAuth Credentials

#### Step 1: Go to Google Cloud Console

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project:
   - Click "Select a Project" → "New Project"
   - Name: `AGI Desktop Agent` (or similar)
   - Click "Create"

#### Step 2: Enable Required APIs

1. In the Console, go to **APIs & Services** → **Library**
2. Search for and enable the following APIs:
   - **Gmail API**: Search → Click → "Enable"
   - **Google Calendar API**: Search → Click → "Enable"

#### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. If prompted for consent screen, click "Configure Consent Screen":
   - Select **User Type: External**
   - Fill in app name, support email
   - Add your email as a test user
   - Click "Save & Continue" through next screens
4. Back to Credentials, click **Create Credentials** → **OAuth 2.0 Client ID** again
5. Choose **Application Type: Desktop app**
6. Click "Create"

#### Step 4: Download Credentials JSON

1. Click the download icon for your created OAuth Client ID
2. Rename the file to **`google_credentials.json`**
3. Move it to: `agi-desktop-agent/config/google_credentials.json`

```bash
# Example (Windows)
Move-Item "C:\Users\YourName\Downloads\client_secret_*.json" "config\google_credentials.json"

# Example (macOS/Linux)
mv ~/Downloads/client_secret_*.json config/google_credentials.json
```

### 3. Enable Google APIs in Configuration

Edit `config/.env`:

```dotenv
ENABLE_GOOGLE_APIS=true
GOOGLE_CREDENTIALS_FILE=config/google_credentials.json
GOOGLE_TOKEN_CACHE_DIR=data/.google_tokens
```

### 4. First-Time Authentication

When you run the app for the first time with `ENABLE_GOOGLE_APIS=true`:

```bash
python -m streamlit run src/ui/app.py
```

A browser window will open asking you to sign in to your Google account and authorize the app. After you click "Allow":
- A token will be automatically cached in `data/.google_tokens/`
- Future runs will use the cached token (no re-auth needed)

## How It Works

### Email Integration

The system will now:

1. **Fetch emails from Gmail** when you ask about a company
2. **Search by company name**: "Prepare for a TechCorp meeting"
   - Automatically searches Gmail for emails mentioning "TechCorp"
   - Fetches up to 15 recent emails
   - Maps to the standard email schema

3. **Fallback to cache**: If Gmail is unavailable, uses `data/emails/cache.json`

### Calendar Integration

The system will now:

1. **Fetch calendar events from Google Calendar** when preparing meetings
2. **Search upcoming events**: "Prepare for a Google meeting"
   - Searches the next 30 days for matching events
   - Searches past 90 days for completed meetings
   - Maps to the meeting schema

3. **Fallback to cache**: If Calendar is unavailable, uses `data/conversations/history.json`

## Architecture

```
MemoryStore (main API)
  ├── search_emails(company)
  │   ├─ Try: GmailClient.search_emails_by_company()  [Fetch from Gmail]
  │   └─ Fallback: Load from data/emails/cache.json
  │
  └── search_conversations(company)
      ├─ Try: CalendarClient.fetch_*_events() [Fetch from Calendar]
      └─ Fallback: Load from data/conversations/history.json
```

## File Structure

```
agi-desktop-agent/
├── config/
│   ├── google_credentials.json        # Downloaded OAuth credentials (don't commit!)
│   ├── .env                           # Local config (ENABLE_GOOGLE_APIS=true)
│   └── .env.example                   # Template
├── data/
│   ├── .google_tokens/
│   │   └── google_token.pickle        # Auto-cached auth token
│   ├── emails/cache.json              # Fallback email cache
│   └── conversations/history.json     # Fallback meeting cache
└── src/
    └── integrations/
        ├── __init__.py
        ├── google_auth.py             # OAuth 2.0 handler
        ├── gmail_client.py            # Gmail API wrapper
        └── calendar_client.py         # Google Calendar API wrapper
```

## Troubleshooting

### Issue: "Google credentials not found"

**Solution**: Make sure `config/google_credentials.json` exists and `ENABLE_GOOGLE_APIS=true`

```bash
# Check if file exists
ls -la config/google_credentials.json  # macOS/Linux
dir config\google_credentials.json      # Windows
```

### Issue: "403 Forbidden" or permission errors

**Solution**: Make sure the provided OAuth credentials enable:
- Gmail API (readonly scope)
- Google Calendar API (readonly scope)

Regenerate credentials and ensure these APIs are enabled in Google Cloud Console.

### Issue: Authentication popup never closes

**Solution**: Check your browser for permission to allow the auth, or:
1. Delete `data/.google_tokens/google_token.pickle`
2. Re-run the app to get fresh auth prompt

### Issue: "python-dateutil not found"

**Solution**:
```bash
pip install python-dateutil==2.8.2
```

## Security Considerations

- **Never commit** `config/google_credentials.json` to Git
- **Never share** `data/.google_tokens/google_token.pickle` (contains auth tokens)
- **Always use** readonly scopes (Gmail API: `gmail.readonly`, Calendar API: `calendar.readonly`)
- The app requests no write permissions to Gmail or Calendar

To revoke access at any time:
1. Delete `data/.google_tokens/google_token.pickle`
2. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
3. Find "AGI Desktop Agent" and click "Remove access"

## Testing

After setup, test the integration:

```bash
cd agi-desktop-agent
python -c "
from src.integrations.google_auth import GoogleAuthHandler
from src.integrations.gmail_client import GmailClient

auth = GoogleAuthHandler()
creds = auth.authenticate()
gmail = GmailClient(auth)
emails = gmail.fetch_recent_emails(max_results=5)
for e in emails:
    print(f'{e[\"date\"]} | {e[\"from\"]} | {e[\"subject\"]}')
"
```

## Disabling Google APIs

To disable Google APIs and use only cache files:

```dotenv
# In config/.env
ENABLE_GOOGLE_APIS=false
```

The app will automatically fall back to `data/emails/cache.json` and `data/conversations/history.json`.

## Next Steps

Once Gmail/Calendar integration is working:

1. **Test with real data**: Ask "Prepare me for [your company] meeting"
   - Should fetch your real email history
   - Should fetch your real upcoming meetings

2. **Prepare for Email Agent integration**: The Email Agent (Scenario 1) will now:
   - Automatically find company emails from Gmail
   - Draft contextual replies using real conversation history

3. **Prepare for Document Agent integration**: The Document Agent (Scenario 2) can:
   - Reference past company documents if stored in Gmail
   - Cross-reference with meeting notes from Calendar

## Questions?

Refer to:
- [Google Calendar API Docs](https://developers.google.com/calendar)
- [Gmail API Docs](https://developers.google.com/gmail/api)
- [OAuth 2.0 Setup Guide](https://developers.google.com/workspace/guides/create-credentials)
