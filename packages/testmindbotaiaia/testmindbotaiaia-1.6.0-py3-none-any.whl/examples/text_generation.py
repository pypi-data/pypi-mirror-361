from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)
    
    model = "mindbot-1.8-ultra"
    response = bot.ask("who are you?")
    print(f"Response:> {response}")
    
    response = bot.generate_content("What is the capital of France?", model=model)
    print(f"Response to 'What is the capital of France?': {response}")
