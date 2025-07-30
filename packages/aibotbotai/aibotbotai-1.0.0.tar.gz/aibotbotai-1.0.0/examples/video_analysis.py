from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

# --- Video File Analysis ---
# Create a dummy video file for testing
with open("sample.mp4", "w") as f:
    f.write("dummy video data")
    
model = "mindvision-flash"
print(f"--- Video File Analysis (Model: {model}) ---")
response = bot.vision.analyze_video("sample.mp4", "Summarize this video.", model=model)
print(f"Video analysis response: {response}")
