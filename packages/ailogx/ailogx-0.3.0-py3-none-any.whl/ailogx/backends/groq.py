import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze(text: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert AI log summarizer for large-scale systems. "
                    "Your job is to analyze deeply nested JSONL logs and extract:\n\n"
                    "1. 🔁 **Patterns**: Repeated events, behaviors, or structures\n"
                    "2. 🧠 **Decisions**: Important choices or branching logic in the logs\n"
                    "3. ❌ **Errors**: Failures, exceptions, and error reasoning\n"
                    "4. 💡 **Insights**: Any behavior, anomaly, or system design clue\n\n"
                    "Provide a clean, structured summary with headings. If relevant, include numbered bullet points under each heading.\n"
                    "Be precise, avoid quoting full logs, and infer intent where applicable."
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
