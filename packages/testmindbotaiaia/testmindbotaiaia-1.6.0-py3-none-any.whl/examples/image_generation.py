from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    model = "mindpaint-2.5"
    print(f"--- Image Generation (Model: {model}) ---")
    status, file_path, link = bot.image.generate_image("a cat sitting on a car", model=model)
    print(f"Image generation status: {status}")
    print(f"Image saved to: {file_path}")
    print(f"Image link: {link}")
