import PIL.Image
from google import genai
from google.genai import types

# 1. Setup your API Key
client = genai.Client(api_key='AIzaSyBEsvNHLy3Sv3r66sF3wakdPAM_uDkDD48')

def generate_from_image(image_path, prompt):
    print(f"\n--- Testing Image + Text (Multimodal) ---")
    img = PIL.Image.open(image_path)
    
    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=[img, prompt]
    )
    print(f"Response: {response.text}")

def summarize_pdf(pdf_path):
    print(f"\n--- Summarizing PDF: {pdf_path} ---")
    # FIX: Changed 'path=' to 'file='
    doc = client.files.upload(file=pdf_path)
    
    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=[doc, "Summarize this document in exactly 50 words."]
    )
    print(f"Summary: {response.text}")


# --- Execution ---

# Ensure these files exist in your folder before running
try:
    # 1. PDF Summarization
    summarize_pdf('report.pdf')

except Exception as e:
    print(f"An error occurred: {e}")
