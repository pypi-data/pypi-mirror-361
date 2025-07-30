import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze(text: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a code log summarizer. Summarize patterns, decisions, errors, and insights from deeply nested JSONL logs."},
            {"role": "user", "content": text}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
