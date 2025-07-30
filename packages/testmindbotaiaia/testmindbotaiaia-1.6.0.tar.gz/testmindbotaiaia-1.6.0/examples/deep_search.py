from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # --- Deep Search ---
    model = "deepsearch-1.0"
    print(f"--- Deep Search (Model: {model}) ---")
    response = bot.search.browse("Compare the latest AI models from Google, OpenAI, and Anthropic.", model=model)
    print(f"Deep search response: {response}")
