from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    model = "mindthink-a3"
    print(f"--- Thinking API (Model: {model}) ---")
    # This prompt is long enough to trigger the thinking model automatically
    long_prompt = "Explain the theory of relativity in simple terms, suitable for a high school student. Cover the main concepts of special and general relativity, and provide some real-world examples of their applications."
    response = bot.generate_content(long_prompt)
    print(f"Response with automatic thinking: {response}")

    # You can also force thinking mode with the 'think' parameter
    response = bot.generate_content("How does AI work?", think=True)
    print(f"Response with forced thinking: {response}")
