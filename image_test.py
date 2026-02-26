from openai import OpenAI
import base64
import os
from datetime import datetime

from dotenv import load_dotenv
from utils import get_executable_dir

env_path = os.path.join(get_executable_dir(), '.env')
load_dotenv(dotenv_path=env_path)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Generate an image
response = client.chat.completions.create(
    model="bytedance-seed/seedream-4.5",
    messages=[
        {
            "role": "user",
            "content": "Generate a beautiful sunset over mountains"
        }
    ],
    extra_body={"modalities": ["image", "text"]}
)

# Extract the assistant message
message = response.choices[0].message

if message.images:
    for idx, image in enumerate(message.images):
        data_url = image["image_url"]["url"]

        # Remove data URL prefix
        header, encoded = data_url.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        # Get Downloads folder
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

        # Create unique filename
        filename = f"seedream_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}.png"
        file_path = os.path.join(downloads_path, filename)

        # Save image
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        print(f" Image saved to: {file_path}")
else:
    print(" No images returned")
