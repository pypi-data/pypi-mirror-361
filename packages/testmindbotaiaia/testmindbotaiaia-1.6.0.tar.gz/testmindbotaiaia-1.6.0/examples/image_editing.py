from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # Create a dummy image file for testing
    with open("sample.jpg", "w") as f:
        f.write("dummy image data")

    model = "mindstyle-2.5"
    print(f"--- Image Editing (Model: {model}) ---")
    text_response, file_path = bot.image.edit_image("sample.jpg", "add a hat on the cat", model=model)
    print(f"Image editing text response: {text_response}")
    print(f"Edited image saved to: {file_path}")
