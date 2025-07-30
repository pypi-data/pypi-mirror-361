from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # --- YouTube Video Analysis ---
    model = "mindtube-1.0"
    print(f"--- YouTube Video Analysis (Model: {model}) ---")
    youtube_url = "https://www.youtube.com/watch?v=9hE5-98ZeCg"
    response = bot.vision.analyze_youtube_video(youtube_url, "Please summarize the video in 3 sentences.", model=model)
    print(f"YouTube analysis response: {response}")
