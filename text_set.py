"""
Quick test script to confirm Groq (LLM) and Tavily (search) API keys work.
Run this with: python test_setup.py
"""

import os
from dotenv import load_dotenv

# Load keys from .env file
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

print("Checking that keys were loaded from .env...")
print("GROQ_API_KEY found:", bool(groq_key))
print("TAVILY_API_KEY found:", bool(tavily_key))
print()

# Test Groq (LLM)
print("Testing Groq API...")
try:
    from groq import Groq

    client = Groq(api_key=groq_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say hello in exactly 5 words."}],
    )
    print("Groq works! Response:", response.choices[0].message.content)
except Exception as e:
    print("Groq FAILED:", e)

print()

# Test Tavily (search)
print("Testing Tavily API...")
try:
    from tavily import TavilyClient

    tavily_client = TavilyClient(api_key=tavily_key)
    result = tavily_client.search(query="latest AI news")
    print("Tavily works! First result title:", result["results"][0]["title"])
except Exception as e:
    print("Tavily FAILED:", e)