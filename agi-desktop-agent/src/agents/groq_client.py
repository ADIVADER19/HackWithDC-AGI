"""
Groq API Client - Llama 3.3 70B Integration
Developer 1: Backend Agents
"""

import os
from groq import Groq
from dotenv import load_dotenv

# Use absolute path so it works regardless of cwd
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
load_dotenv(os.path.join(_project_root, 'config', '.env'))

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.client = Groq(api_key=self.api_key)
    
    def chat(self, messages, tools=None, temperature=0.7):
        """
        Send chat request to Groq
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            tools: Optional list of tool definitions for function calling
            temperature: Model temperature (0-1)
        
        Returns:
            Response dict with content and optional tool_calls
        """
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": int(os.getenv('MAX_TOKENS', 4096))
            }
            
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**params)
            
            return {
                "content": response.choices[0].message.content,
                "tool_calls": response.choices[0].message.tool_calls if hasattr(response.choices[0].message, 'tool_calls') else None,
                "finish_reason": response.choices[0].finish_reason
            }
        
        except Exception as e:
            print(f"Groq API Error: {e}")
            return {"content": None, "error": str(e)}
    
    def test_connection(self):
        """Test if Groq API is working"""
        test_response = self.chat([{"role": "user", "content": "Hello, respond with 'OK'"}])
        return "OK" in (test_response.get("content") or "")


# Quick test
if __name__ == "__main__":
    client = GroqClient()
    if client.test_connection():
        print("✅ Groq API connection successful!")
    else:
        print("❌ Groq API connection failed")
