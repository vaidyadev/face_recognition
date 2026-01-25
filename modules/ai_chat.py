import os
import json
import base64
from datetime import datetime
from openai import OpenAI
import PIL.Image
from google import genai
from .database import load_attendance_data

# Initialize Clients
# OpenRouter Client
# Start of imports
import openai
from openai import OpenAI
import PIL.Image
from google import genai
from .database import load_attendance_data

# Initialize Clients
# OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Google GenAI Client
google_client = genai.Client(api_key='AIzaSyBEsvNHLy3Sv3r66sF3wakdPAM_uDkDD48')

def load_cache(cache_file):
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
            return {}
    return {}

def save_cache(cache_file, response_cache):
    try:
        with open(cache_file, 'w') as f:
            json.dump(response_cache, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

def load_faq_context():
    try:
        with open("faq.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "FAQ file not found."

def handle_multimodal_gemini(prompt, attachments):
    try:
        print(f"DEBUG: Using Model -> gemini-2.5-flash-lite (Multimodal) for {len(attachments)} attachments")
        contents = []
        
        # Add Prompt first or last? contents list order matters.
        # Usually prompt is text.
        
        for path in attachments:
            if not os.path.exists(path):
                continue
                
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico']:
                img = PIL.Image.open(path)
                contents.append(img)
            elif ext in ['.pdf', '.txt', '.py', '.json', '.docx']:
                try:
                    uploaded_file = google_client.files.upload(file=path)
                    contents.append(uploaded_file)
                except Exception as up_e:
                    print(f"Upload failed for {path}: {up_e}")
        
        contents.append(prompt)
        
        response = google_client.models.generate_content(
            model='gemini-2.5-flash-lite-preview-09-2025', 
            contents=contents
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "ResourceExhausted" in error_msg:
             return "⚠️ **Gemini Error**: Free tier limit reached (429). Please wait a while or switch models."
        return f"Gemini Error: {error_msg}"

def handle_image_generation(prompt, attachments=None):
    try:
        print("DEBUG: Using Model -> bytedance-seed/seedream-4.5 (Image Generation)")
        
        messages = []
        user_content = []
        
        # Add text prompt
        user_content.append({"type": "text", "text": prompt})
        
        # Add image attachments if any (for editing/variation)
        if attachments:
            for path in attachments:
                if not os.path.exists(path): continue
                
                ext = os.path.splitext(path)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico']:
                    try:
                        with open(path, "rb") as image_file:
                             base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                             user_content.append({
                                 "type": "image_url",
                                 "image_url": {
                                     "url": f"data:image/{ext[1:]};base64,{base64_image}"
                                 }
                             })
                    except Exception as e:
                        print(f"Error encoding image {path}: {e}")

        messages.append({
            "role": "user",
            "content": user_content
        })

        response = client.chat.completions.create(
            model="bytedance-seed/seedream-4.5",
            messages=messages,
            extra_body={"modalities": ["image", "text"]} 
        )
        
        message = response.choices[0].message
        
        saved_paths = []
        if message.images:
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_path, exist_ok=True)
            
            for idx, image in enumerate(message.images):
                data_url = image["image_url"]["url"]
                header, encoded = data_url.split(",", 1)
                image_bytes = base64.b64decode(encoded)
                
                filename = f"gen_img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}.png"
                file_path = os.path.join(downloads_path, filename)
                
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                saved_paths.append(file_path)
            
            return f"[IMAGE_GENERATED]: {saved_paths[0]}"
        else:
             # Fallback if it returned text
             return message.content or "No image generated."
             
    except openai.APIStatusError as e:
        if e.status_code == 402:
             return "⚠️ **SeedDream Error**: Insufficient credits or limit reached (402 Payment Required)."
        return f"Image Gen Error (API): {str(e)}"
    except Exception as e:
        return f"Image Gen Error: {str(e)}"


def ask_openai(prompt, session_messages, response_cache, cache_file, attachments=None, model_name=None):
    try:
        lower_prompt = prompt.lower()
        
        
        if model_name and ('gemini' in model_name.lower() or 'google' in model_name.lower()):
            # if attachments and len(attachments) > 0:
                 return handle_multimodal_gemini(prompt, attachments)

        if model_name and 'seedream' in model_name.lower():
             return handle_image_generation(prompt, attachments)
        
        
        current_context_messages = session_messages[:] # Copy
        current_context_messages.append({"role": "user", "content": prompt})
        
        attendance_context = load_attendance_data()
        faq_context = load_faq_context()

        # Combine system + last 10 turns of context
        messages = [
            {
                "role": "system",
                "content": (
                    "You are HelpBot, a smart, polite, and helpful desktop female assistant.\n\n"

                    "IMPORTANT RENDERER INSTRUCTIONS (STRICT):\n"
                    "1. The user's GUI does NOT support Markdown bold (**text**) or italics (*text*). DO NOT USE THEM.\n"
                    "2. Do NOT use using asterisks (*) for lists. ALWAYS use numbered lists (e.g. '1. Step one').\n"
                    "3. For math, ALWAYS use LaTeX inside $$ (block) or \\( (inline). Example: $$E=mc^2$$.\n"
                    "4. For tables, ALWAYS use standard Markdown format with | separators, a header row, and a dash separator row (e.g. |---|). Ensure every row starts and ends with |.\n"
                    "5. Do NOT use literal * or / symbols in text unless it is for math equations or file paths.\n"
                    "6. Code blocks with ```language are supported and encouraged.\n\n"

                    "GENERAL RULES:\n"
                    "1. You are given an FAQ document below.\n"
                    "2. If the user's question is related to HelpBot, the system, features, usage, or behavior, "
                    "refer to the FAQ.\n"
                    "3. If the answer is not in the FAQ, say 'I am not sure about that currently.'\n"
                    "4. Do NOT invent answers for system-related questions.\n"
                    "5. For non-system questions (coding, math, general knowledge), answer normally.\n\n"
                    "FAQ DOCUMENT:\n"
                    f"{faq_context}\n\n"
                    "Attendance Data (use only if attendance is asked):\n"
                    f"{attendance_context}\n"
                )
            }
        ] + current_context_messages[-10:]

        # Check cache first (only for text chat)
        # We probably shouldn't cache different models' responses for same prompt mixed up, 
        # but for now let's keep it simple or skip cache if model changed?
        # Let's use cache key = prompt + model_name to be safe?
        # Or just skip cache update if not default?
        # Reusing existing cache logic for now.
        
        if prompt in response_cache:
            return response_cache[prompt]

        # Use provided model name from settings or default
        selected_model = model_name or "tngtech/deepseek-r1t2-chimera:free"
        print(f"DEBUG: Using Model -> {selected_model}")
        
        # Make OpenAI API request
        completion = client.chat.completions.create(
            extra_headers={"X-Title": "HelpBot"},
            model=selected_model,
            messages=messages
        )

        response = completion.choices[0].message.content.strip()

        # --- Long Response Caching ---
        word_count = len(response.split())
        if word_count >= 200:
            response_cache[prompt] = response

            # Enforce max 10 cache entries
            if len(response_cache) > 10:
                first_key = next(iter(response_cache))
                del response_cache[first_key]

            save_cache(cache_file, response_cache)

        return response

        return response

    except openai.APIStatusError as e:
        if e.status_code == 402:
             return "⚠️ **OpenRouter Error**: Insufficient credits or payment required (402)."
        print(e)
        return f"OpenRouter status error: {str(e)}"
    except Exception as e:
        print(e)
        return f"OpenRouter error: {str(e)}"

def convert_history_to_gemini(messages):
    """Converts OpenAI message format to Gemini history format with System Context."""
    history = []
    
    # Loads Contexts
    attendance_context = load_attendance_data()
    faq_context = load_faq_context()
    
    system_text = (
        "You are HelpBot, a smart, polite, and helpful desktop female assistant.\n\n"
        "IMPORTANT RENDERER INSTRUCTIONS (STRICT):\n"
        "1. The user's GUI does NOT support Markdown bold (**text**) or italics (*text*). DO NOT USE THEM.\n"
        "2. Do NOT use using asterisks (*) for lists. ALWAYS use numbered lists (e.g. '1. Step one').\n"
        "3. For math, ALWAYS use LaTeX inside $$ (block) or \\( (inline). Example: $$E=mc^2$$.\n"
        "4. For tables, ALWAYS use standard Markdown format with | separators, a header row, and a dash separator row (e.g. |---|). Ensure every row starts and ends with |.\n"
        "5. Do NOT use literal * or / symbols in text unless it is for math equations or file paths.\n"
        "6. Code blocks with ```language are supported and encouraged.\n\n"
        "GENERAL RULES:\n"
        "1. You are given an FAQ document below.\n"
        "2. If the user's question is related to HelpBot, the system, features, usage, or behavior, refer to the FAQ.\n"
        "3. If the answer is not in the FAQ, say 'I am not sure about that currently.'\n"
        "4. Do NOT invent answers for system-related questions.\n"
        "5. For non-system questions (coding, math, general knowledge), answer normally.\n\n"
        "FAQ DOCUMENT:\n"
        f"{faq_context}\n\n"
        "Attendance Data (use only if attendance is asked):\n"
        f"{attendance_context}\n"
    )

    # Inject System Context as the first interaction
    history.append({"role": "user", "parts": [{"text": system_text}]})
    history.append({"role": "model", "parts": [{"text": "Understood. I will follow these instructions and use the provided context."}]})

    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        history.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
    
    # Ensure history ends with 'model' if we are about to send a new user message?
    # No, 'history' passed to create logic sets up the *past*. 
    # The next action will be send_message (User).
    # So history must end with 'model' (or allow user->user if API supports it, but simple alternation is safest).
    # If the last message in `messages` was 'user', we might have an issue if we just append it and then send another user message?
    # But `session_messages` usually ends with 'assistant' (last turn). 
    # If `session_messages` includes the *pending* user message, then we have a problem.
    # In 'chatbot2.py', `self.session_messages` typically contains confirmed history.
    # The *current* `user_input` is passed separately to `ask_gemini_chat`.
    # So `messages` should end with 'assistant' (model).
    # If `messages` is empty, we just have our system prompt interaction.
    
    return history

def create_gemini_chat(history=None):
    try:
        # Create a new chat session
        chat = google_client.chats.create(
            model='gemini-2.5-flash-lite-preview-09-2025',
            history=history if history else []
        ) 
        return chat
    except Exception as e:
        print(f"Error creating Gemini chat: {e}")
        return None

def ask_gemini_chat(chat_session, prompt, attachments=None):
    try:
        print("DEBUG: Using Model -> gemini-2.5-flash-lite(Sticky Session)")
        contents = []
        
        # Add attachments to contents
        if attachments:
            for path in attachments:
                if not os.path.exists(path): continue
                
                ext = os.path.splitext(path)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico']:
                    img = PIL.Image.open(path)
                    contents.append(img)
                elif ext in ['.pdf', '.txt', '.py', '.json', '.docx']:
                    try:
                        uploaded_file = google_client.files.upload(file=path)
                        contents.append(uploaded_file)
                    except Exception as up_e:
                        print(f"Upload failed for {path}: {up_e}")

        # Add prompt text
        contents.append(prompt)
        
        response = chat_session.send_message(contents)
        return response.text
        response = chat_session.send_message(contents)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "ResourceExhausted" in error_msg:
             return "⚠️ **Gemini Error**: Free tier limit reached (429). Please wait a while."
        return f"Gemini Session Error: {error_msg}"
