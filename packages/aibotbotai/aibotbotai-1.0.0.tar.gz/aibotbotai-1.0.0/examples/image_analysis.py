from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

# Create a dummy image file for testing
with open("sample.jpg", "w") as f:
    f.write("dummy image data")
    
model = "mindvision-flash"
print(f"--- Image Understanding (Model: {model}) ---")
response = bot.vision.analyze_image("sample.jpg", "Caption this image.", model=model)
print(f"Image analysis response: {response}")
