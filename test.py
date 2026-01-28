import PIL.Image
from google import genai
from google.genai import types
import time
# 1. Setup your API Key
client = genai.Client(api_key='AIzaSyDkmTUS7YoGTj1sukc9pwSAUhdeK--ePz8')

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
        model='gemini-2.5-flash-lite-preview-09-2025',
        contents=[doc, "Summarize this document in exactly 50 words."]
    )
    print(f"Summary: {response.text}")

def test_audio_input(audio_path):
    print(f"\n--- Testing Audio: {audio_path} ---")
    # Upload the audio file (e.g., .mp3, .wav)
    audio_file = client.files.upload(file=audio_path)
    
    # Optional: Wait for processing if the file is large
    # For short clips, it's usually ready immediately
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite-preview-09-2025',
        contents=["Provide a transcript and describe the mood of this audio.",audio_file,]
    )
    print(f"Audio Analysis: {response.text}")

def test_video_input(video_path):
    print(f"\n--- Testing Video: {video_path} ---")
    # Upload the video file (e.g., .mp4, .mov)
    video_file = client.files.upload(file=video_path)
    
    # Video files often require a moment to process
    print("Waiting for video processing...")
    while video_file.state.name == "PROCESSING":
        time.sleep(2)
        video_file = client.files.get(name=video_file.name)
    
    if video_file.state.name == "FAILED":
        raise ValueError("Video processing failed.")

    response = client.models.generate_content(
        model='gemini-2.5-flash-lite-preview-09-2025',
        contents=[video_file, "Summarize what happens in this video."]
    )
    print(f"Video Summary: {response.text}")


# --- Execution ---

# Ensure these files exist in your folder before running
try:
    # 1. PDF Summarization
    # summarize_pdf('report.pdf')
    # test_audio_input('download.wav')
    test_video_input('test.mp4')

except Exception as e:
    print(f"An error occurred: {e}")
from google import genai
from google.genai import types

client = genai.Client(api_key='AIzaSyDkmTUS7YoGTj1sukc9pwSAUhdeK--ePz8')

grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

config = types.GenerateContentConfig(
    tools=[grounding_tool]
)

response = client.models.generate_content(
    model="gemini-2.5-flash-lite-preview-09-2025",
    contents="Current share price of tesla",
    config=config,
)

print(response.text)