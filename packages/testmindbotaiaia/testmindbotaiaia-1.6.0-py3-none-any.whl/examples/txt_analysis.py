from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # --- TXT File Analysis ---
    model = "mindbot-1.8-ultra"
    print(f"--- TXT File Analysis (Model: {model}) ---")
    with open("sample.txt", "w") as f:
        f.write("This is a sample text file for analysis. It contains some text about MindBot AI.")
    response = bot.text.analyze_txt("sample.txt", "Summarize this document.", model=model)
    print(f"TXT analysis response: {response}")
