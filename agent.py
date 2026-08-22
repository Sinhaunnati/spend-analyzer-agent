import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import get_total_by_category, find_duplicate_charges, find_unusual_transactions

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

tools = [get_total_by_category, find_duplicate_charges, find_unusual_transactions]

chat = client.chats.create(
    model="gemini-3.6-flash",
    config=types.GenerateContentConfig(tools=tools),
)

print("Spend Analyzer Agent — ask me about your spending. Type 'quit' to exit.\n")

while True:
    question = input("You: ").strip()
    if not question:
        continue
    if question.lower() in ("quit", "exit"):
        break

    response = chat.send_message(question)
    print("Agent:", response.text)
    print()