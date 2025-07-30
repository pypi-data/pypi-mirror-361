import tiktoken
import json

MODEL_TOKEN_LIMITS = {
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4096,
    "mixtral-8x7b-32768": 32768,
    "llama3": 8192,  # Approx, for Ollama
}

def get_token_count(text: str, model="gpt-4") -> int:
    enc = tiktoken.encoding_for_model(model) if "gpt" in model else tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def chunk_by_tokens(logs, model="gpt-4", max_tokens=3000):
    chunks = []
    current = []
    current_tokens = 0

    for log in logs:
        line = log if isinstance(log, str) else json.dumps(log)
        tokens = get_token_count(line, model)

        if current_tokens + tokens > max_tokens:
            chunks.append(current)
            current = [line]
            current_tokens = tokens
        else:
            current.append(line)
            current_tokens += tokens

    if current:
        chunks.append(current)
    return chunks
