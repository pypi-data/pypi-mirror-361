from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # --- Video File Analysis ---
    # Create a dummy video file for testing
    with open("sample.mp4", "w") as f:
        f.write("dummy video data")
        
    model = "mindvision-flash"
    print(f"--- Video File Analysis (Model: {model}) ---")
    response = bot.vision.analyze_video("sample.mp4", "Summarize this video.", model=model)
    print(f"Video analysis response: {response}")
