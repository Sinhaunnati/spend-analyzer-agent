import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import your real, tested functions
from tools import get_total_by_category, find_duplicate_charges, find_unusual_transactions

# Set up the look of the web page
st.set_page_config(page_title="Spend Analyzer AI", page_icon="💳", layout="wide")

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("`GEMINI_API_KEY` not found in `.env` file. Please check your setup.")
    st.stop()

# Initialize the Gemini Chat Agent (only runs once per session)
if "chat" not in st.session_state:
    # Fix: Save the client to session_state so it stays open!
    st.session_state.client = genai.Client(api_key=api_key)
    
    # Give the agent access to the real Python tools
    tools = [get_total_by_category, find_duplicate_charges, find_unusual_transactions]
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-3.6-flash", 
        config=types.GenerateContentConfig(tools=tools),
    )

# Create a place to store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Data Overview ---
with st.sidebar:
    st.header("📊 Transaction Overview")
    try:
        # Load the categorized CSV data
        df = pd.read_csv("data/transactions_categorized.csv")
        st.metric(label="Total Transactions", value=len(df))
        st.metric(label="Total Spent", value=f"₹{df['amount'].sum():,.2f}")
        
        # Add a dropdown to view the raw data
        with st.expander("🔍 View All Categorized Data", expanded=False):
      st.dataframe(df, width="stretch", height=300)
           
    except Exception as e:
        st.error(f"Could not load transaction data: {e}")

    st.markdown("---")
    st.markdown("### 💡 Try asking:")
    st.markdown("- *\"How much did I spend on food?\"*")
    st.markdown("- *\"Did I get charged twice for anything?\"*")
    st.markdown("- *\"Are there any unusually large transactions?\"*")

# --- Main Page: Chat Interface ---
st.title("💳 AI Finance Controller")
st.caption("Powered by Gemini function-calling on real bank data.")

# Display all previous messages in the chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# The input box where you type questions
if prompt := st.chat_input("Ask a question about your spending..."):
    # Save and show what the user typed
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ask Gemini and run the tools
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your data..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                reply = response.text
            except Exception as e:
                reply = f"Error generating response: {e}"
            
            # Show the final answer and save it to history
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})