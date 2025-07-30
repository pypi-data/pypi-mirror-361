from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

model = "mindbot-1.8-ultra"
response = bot.ask("who are you?")
print(f"Response:> {response}")

response = bot.generate_content("What is the capital of France?", model=model)
print(f"Response to 'What is the capital of France?': {response}")
