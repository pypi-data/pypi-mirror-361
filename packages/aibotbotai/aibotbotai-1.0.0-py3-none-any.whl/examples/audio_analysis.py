from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

# --- Audio File Analysis ---
# Create a dummy audio file for testing
with open("sample.mp3", "w") as f:
    f.write("dummy audio data")
    
model = "mindaudio-pro"
print(f"--- Audio File Analysis (Model: {model}) ---")
response = bot.audio.analyze_audio("sample.mp3", "Describe this audio clip.", model=model)
print(f"Audio analysis response: {response}")
