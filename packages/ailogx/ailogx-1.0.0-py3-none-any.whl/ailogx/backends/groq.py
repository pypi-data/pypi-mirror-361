import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze(text: str, model: str = "llama-3.3-70b-versatile") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
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
        temperature=0.3,
    )
    return response.choices[0].message.content
