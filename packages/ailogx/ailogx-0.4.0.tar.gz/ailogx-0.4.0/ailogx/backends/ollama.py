import requests

def analyze(text: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "gemma3",  # Or use mistral, codellama, etc.
            "messages": [
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
            "stream": False
        }
    )
    # print(f"response = {response.json()}")
    return response.json()["message"]["content"]
