from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # --- Audio File Analysis ---
    # Create a dummy audio file for testing
    with open("sample.mp3", "w") as f:
        f.write("dummy audio data")
        
    model = "mindaudio-pro"
    print(f"--- Audio File Analysis (Model: {model}) ---")
    response = bot.audio.analyze_audio("sample.mp3", "Describe this audio clip.", model=model)
    print(f"Audio analysis response: {response}")
