import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CATEGORIES = [
    "Rent", "Subscriptions", "Utilities", "Food & Dining", "Groceries",
    "Transport", "Shopping", "Entertainment", "Health & Fitness",
    "Healthcare", "UPI Transfer",
]

df = pd.read_csv("data/transactions.csv")

# Build one batch prompt with ALL transactions, asking for a category per
# txn_id. Doing it as one batch (not 164 separate API calls) is faster and
# lets the model see everything at once for more consistent labeling.
transaction_list = "\n".join(
    f"{row.txn_id}: {row.merchant} | {row.description} | ₹{row.amount} | {row.mode}"
    for row in df.itertuples()
)

prompt = f"""
You are categorizing bank transactions. Choose EXACTLY ONE category per
transaction from this fixed list, nothing else:
{", ".join(CATEGORIES)}

Transactions:
{transaction_list}

Respond with ONLY a JSON object mapping each txn_id to its category, like:
{{"TXN1001": "Food & Dining", "TXN1002": "Rent"}}
No explanation, no markdown formatting, just the raw JSON object.
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
)

# The model sometimes wraps JSON in ```json ... ``` — strip that if present.
raw = response.text.strip()
if raw.startswith("```"):
    raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

categories = json.loads(raw)

df["category"] = df["txn_id"].map(categories)
df.to_csv("data/transactions_categorized.csv", index=False)

print(f"Categorized {len(df)} transactions.")
print(df[["txn_id", "merchant", "amount", "category"]].head(10))