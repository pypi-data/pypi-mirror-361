from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # Create a dummy image file for testing
    with open("sample.jpg", "w") as f:
        f.write("dummy image data")
        
    model = "mindvision-flash"
    print(f"--- Image Understanding (Model: {model}) ---")
    response = bot.vision.analyze_image("sample.jpg", "Caption this image.", model=model)
    print(f"Image analysis response: {response}")
