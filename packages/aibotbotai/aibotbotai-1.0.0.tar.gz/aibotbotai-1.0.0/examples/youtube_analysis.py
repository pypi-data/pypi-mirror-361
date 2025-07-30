from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

# --- YouTube Video Analysis ---
model = "mindtube-1.0"
print(f"--- YouTube Video Analysis (Model: {model}) ---")
youtube_url = "https://www.youtube.com/watch?v=9hE5-98ZeCg"
response = bot.vision.analyze_youtube_video(youtube_url, "Please summarize the video in 3 sentences.", model=model)
print(f"YouTube analysis response: {response}")
