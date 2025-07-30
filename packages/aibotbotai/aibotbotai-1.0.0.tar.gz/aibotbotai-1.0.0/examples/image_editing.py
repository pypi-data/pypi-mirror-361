from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

# Create a dummy image file for testing
with open("sample.jpg", "w") as f:
    f.write("dummy image data")

model = "mindstyle-2.5"
print(f"--- Image Editing (Model: {model}) ---")
text_response, file_path = bot.image.edit_image("sample.jpg", "add a hat on the cat", model=model)
print(f"Image editing text response: {text_response}")
print(f"Edited image saved to: {file_path}")
