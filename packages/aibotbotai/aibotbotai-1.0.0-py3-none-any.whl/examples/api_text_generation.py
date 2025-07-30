import requests
import json

# Make sure your Flask API is running: python api.py
# Replace "YOUR_GEMINI_API_KEY" in api.py with your actual API key.

api_url = "http://127.0.0.1:5000/ask"

# Example 1: Normal text generation
question1 = "What is the capital of France?"
payload1 = {"question": question1}

response1 = requests.post(api_url, json=payload1)
print(f"Question: {question1}")
print(f"Response: {response1.json()['response']}")

# Example 2: Asking about the bot's identity
question2 = "Who are you?"
payload2 = {"question": question2}

response2 = requests.post(api_url, json=payload2)
print(f"\nQuestion: {question2}")
print(f"Response: {response2.json()['response']}")
