from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

# --- Web Search ---
model = "mindsearch-2.5"
print(f"--- Web Search (Model: {model}) ---")
response = bot.search.browse("What are the latest AI news?", model=model)
print(f"Search response: {response}")
