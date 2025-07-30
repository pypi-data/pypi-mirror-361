from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

# --- TXT File Analysis ---
model = "mindbot-1.8-ultra"
print(f"--- TXT File Analysis (Model: {model}) ---")
with open("sample.txt", "w") as f:
    f.write("This is a sample text file for analysis. It contains some text about MindBot AI.")
response = bot.text.analyze_txt("sample.txt", "Summarize this document.", model=model)
print(f"TXT analysis response: {response}")
