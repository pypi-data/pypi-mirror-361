import hashlib, os, json
from pathlib import Path

CACHE_DIR = Path(".cache/llm_responses")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_key(text: str) -> str:
    return hashlib.sha1(text.encode()).hexdigest()

def get_cached_response(text: str) -> str | None:
    key = get_cache_key(text)
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f).get("response")
    return None

def save_response_to_cache(text: str, response: str):
    key = get_cache_key(text)
    path = CACHE_DIR / f"{key}.json"
    with open(path, "w") as f:
        json.dump({"response": response}, f)
