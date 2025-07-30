from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

model = "mindpaint-2.5"
print(f"--- Image Generation (Model: {model}) ---")
status, file_path, link = bot.image.generate_image("a cat sitting on a car", model=model)
print(f"Image generation status: {status}")
print(f"Image saved to: {file_path}")
print(f"Image link: {link}")
