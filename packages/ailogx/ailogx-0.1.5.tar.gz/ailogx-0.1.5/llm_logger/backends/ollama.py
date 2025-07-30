import requests

def analyze(text: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "gemma3",  # Or use mistral, codellama, etc.
            "messages": [
                {"role": "system", "content": "You summarize structured logs."},
                {"role": "user", "content": text}
            ],
            "stream": False
        }
    )
    # print(f"response = {response.json()}")
    return response.json()["message"]["content"]
