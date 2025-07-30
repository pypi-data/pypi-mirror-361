from mindbot import mind
from config import API_KEY
import pandas as pd

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # --- CSV File Analysis ---
    model = "mindbot-1.8-ultra"
    print(f"--- CSV File Analysis (Model: {model}) ---")
    data = {'product': ['MindBot License', 'MindBot API Access'], 'price': [100, 500]}
    df = pd.DataFrame(data)
    df.to_csv("sample.csv", index=False)
    response = bot.text.analyze_csv("sample.csv", "What is the price of the MindBot License?", model=model)
    print(f"CSV analysis response: {response}")
