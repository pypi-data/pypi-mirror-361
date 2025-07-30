from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

# --- Deep Search ---
model = "deepsearch-1.0"
print(f"--- Deep Search (Model: {model}) ---")
response = bot.search.browse("Compare the latest AI models from Google, OpenAI, and Anthropic.", model=model)
print(f"Deep search response: {response}")
