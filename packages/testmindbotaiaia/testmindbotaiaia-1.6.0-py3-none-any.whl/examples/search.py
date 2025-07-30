from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # --- Web Search ---
    model = "mindsearch-2.5"
    print(f"--- Web Search (Model: {model}) ---")
    response = bot.search.browse("What are the latest AI news?", model=model)
    print(f"Search response: {response}")
