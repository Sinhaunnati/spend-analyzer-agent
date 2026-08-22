import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found — check your .env file")

client = genai.Client(api_key=api_key)

prompt = """
Here is a bank transaction:
Merchant: Zomato
Description: Food delivery
Amount: 474.50 INR

What spending category does this belong to? Answer in one or two words.
"""

response = client.models.generate_content(
     model="gemini-3.6-flash",
    contents=prompt,
)
print("Gemini says:", response.text)