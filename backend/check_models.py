import os
from dotenv import load_dotenv
from google import genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

model_name = "gemini-3.6-flash"

try:
    response = client.models.generate_content(
        model=model_name,
        contents="Explain what a resume is in two sentences."
    )

    print("\nModel test successful!")
    print(response.text)

except Exception as e:
    print("\nModel test failed:")
    print(e)