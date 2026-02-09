"""
Groq API Client - Llama 3.3 70B Integration
Developer 1: Backend Agents
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import openai

# Load .env from the config directory (two levels up from this file)
env_path = Path(__file__).parent.parent.parent / 'config' / '.env'
load_dotenv(env_path)

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        openai.api_key = self.api_key
        openai.api_base = "https://api.groq.com/openai/v1"

    def ask(self, prompt):
        client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=int(os.getenv('MAX_TOKENS', 4096)),
            temperature=0.7,
        )
        return response.choices[0].message.content
