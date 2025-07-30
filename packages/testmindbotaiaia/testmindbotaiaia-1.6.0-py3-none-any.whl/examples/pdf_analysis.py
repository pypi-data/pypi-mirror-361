from mindbot import mind
from config import API_KEY

if not API_KEY or API_KEY == "Your_MindBot_API_Key":
    print("Please set your Gemini API key in the examples/config.py file.")
else:
    bot = mind(api_key=API_KEY)

    # --- PDF File Analysis ---
    # Create a dummy PDF file for testing
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="This is a sample PDF file for analysis.", ln=1, align="C")
        pdf.output("sample.pdf")
        
        model = "mindvision-flash"
        print(f"--- PDF File Analysis (Model: {model}) ---")
        response = bot.vision.analyze_pdf("sample.pdf", "Summarize this document.", model=model)
        print(f"PDF analysis response: {response}")
    except ImportError:
        print("Please install fpdf to run this example: pip install fpdf")
