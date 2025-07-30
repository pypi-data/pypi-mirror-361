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
                    "You are a code log summarizer for developers. Your job is to extract meaningful patterns, errors, and decisions from deeply nested JSONL or JSON logs.\n"
                    "For each issue, include **the file name, function name, and line number** (if present in the log) to help locate the problem in code.\n"
                    "Structure the summary with clear sections: Patterns, Decisions, Errors, Insights, Recommendations, and Code Locations."
                )
            },
            {"role": "user", "content": text}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
