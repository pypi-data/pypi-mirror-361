import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze(text: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a log summarizer for deeply structured JSONL logs."},
            {"role": "user", "content": text}
        ],
        temperature=0.3
    )
    return response['choices'][0]['message']['content']
