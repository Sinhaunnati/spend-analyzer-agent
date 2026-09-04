import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import (
    get_total_by_category, 
    find_duplicate_charges, 
    find_unusual_transactions, 
    get_monthly_comparison,
    run_financial_health_audit,
    check_budget_status,
    search_transactions_by_keyword
)

st.set_page_config(page_title="Spend Analyzer AI", page_icon="💳", layout="wide")

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("`GEMINI_API_KEY` not found in `.env` file. Please check your setup.")
    st.stop()

if "chat" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)
    tools = [
        get_total_by_category, 
        find_duplicate_charges, 
        find_unusual_transactions, 
        get_monthly_comparison,
        run_financial_health_audit,
        check_budget_status,
        search_transactions_by_keyword
    ]
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-3.6-flash", 
        config=types.GenerateContentConfig(tools=tools),
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar ---
with st.sidebar:
    st.header("📊 Transaction Overview")
    try:
        df = pd.read_csv("data/transactions_categorized.csv")
        st.metric(label="Total Transactions", value=len(df))
        st.metric(label="Total Spent", value=f"₹{df['amount'].sum():,.2f}")
        
        st.markdown("### 📈 Spend by Category")
        category_spend = df.groupby('category')['amount'].sum()
        st.bar_chart(category_spend)

        st.markdown("---")
        if st.button("🚀 Run AI CFO Audit", use_container_width=True):
            prompt = "Run a complete financial health audit on my spending."
            st.session_state.messages.append({"role": "user", "content": prompt})
            try:
                response = st.session_state.chat.send_message(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception:
                st.session_state.messages.append({"role": "assistant", "content": "⚠️ Rate limit reached. Please wait 10 seconds."})
            st.rerun()

        report_text = f"RAZORPAY BUILDATHON REPORT\nTotal Spend: ₹{df['amount'].sum():,.2f}"
        st.download_button(
            label="📥 Download Executive Report",
            data=report_text,
            file_name="cfo_report.txt",
            mime="text/plain",
            use_container_width=True
        )

        with st.expander("🔍 View All Categorized Data", expanded=False):
            st.dataframe(df, use_container_width=True, height=300)
    except Exception as e:
        st.error(f"Could not load data: {e}")

    st.markdown("---")
    st.markdown("### 💡 Try copying these:")
    st.markdown("- *\"How much did I spend on food?\"*")
    st.markdown("- *\"Did I get charged twice for anything?\"*")
    st.markdown("- *\"Am I within my ₹60k monthly budget?\"*")

# --- Main Chat Page ---
st.title("💳 AI Finance Controller")
st.caption("Powered by Gemini function-calling on real bank data.")

st.markdown("---")

# Display all previous messages in the chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# The input box where you type questions
if prompt := st.chat_input("Ask a question about your spending..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                reply = response.text
            except Exception:
                reply = "⚠️ API rate limit reached (Free tier quota). Please wait about 10 seconds and try again."
            
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})