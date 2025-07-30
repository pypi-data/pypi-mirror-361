from mindbot import mind

MIND_KEY = "YOUR_MINDBOT_API_KEY_HERE"

mind.config(api_key=MIND_KEY)

bot = mind()

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
