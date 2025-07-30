import requests

def analyze(text: str,  model: str = "gemma3") -> str:
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,  # Or use mistral, codellama, etc.
            "messages": [
                {
                    "role": "system",
                    "content": (
                        """You are a senior LLM log summarizer that converts structured logs into a developer task list.

                        Analyze deeply nested JSON logs and produce a precise summary broken into the following 3 sections:

                        🔥 Failures and Likely Root Causes:
                        - Mention specific errors with file, function, and line if present.
                        - Include reason, frequency, and any observable pattern.

                        🧭 Key Decisions or Conditions:
                        - Summarize decision points (e.g., 'admin access granted') and which code paths were taken.

                        🛠️ Actionable Fix Suggestions:
                        - Group by file + function name.
                        - Write assertive, precise dev tasks (e.g., "Fix reserved username check in auth.py:signup_user").

                        Keep your response concise and optimized for developer time savings.
                        """
                    )
                },
                {"role": "user", "content": text}
            ],
            "stream": False
        }
    )
    # print(f"response = {response.json()}")
    return response.json()["message"]["content"]
