from mindbot import mind
import pandas as pd

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

# --- CSV File Analysis ---
model = "mindbot-1.8-ultra"
print(f"--- CSV File Analysis (Model: {model}) ---")
data = {'product': ['MindBot License', 'MindBot API Access'], 'price': [100, 500]}
df = pd.DataFrame(data)
df.to_csv("sample.csv", index=False)
response = bot.text.analyze_csv("sample.csv", "What is the price of the MindBot License?", model=model)
print(f"CSV analysis response: {response}")
