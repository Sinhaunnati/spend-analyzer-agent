\# Spend Analyzer Agent



An AI agent that understands your real spending data and answers questions

about it in plain English — built for the Razorpay AI Builder Buildathon

(Track: AI Finance Controller).



\## What makes this "agentic," not just a chatbot



Most "AI finance" demos are a thin wrapper: stuff your data into a prompt

and hope the model's text output happens to be right. This project doesn't

do that. Instead, the LLM is given a fixed set of \*\*real Python functions\*\*

and decides, based on your question, which one (or ones) to actually call.

The function runs real code — real pandas math on real transaction data —

and the LLM only sees the true result afterward, which it then explains in

plain language. It can't hallucinate a total; it can only report what the

function actually returned.



\## Architecture

