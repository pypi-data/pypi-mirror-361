# llm_logger/summarizer/cache.py

import hashlib
import os
from pathlib import Path

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)

def hash_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def cache_get(hash_key: str, expiry_seconds: int = 7 * 86400) -> str | None:
    cache_file = CACHE_DIR / f"{hash_key}.txt"
    meta_file = CACHE_DIR / f"{hash_key}.meta"

    if not (cache_file.exists() and meta_file.exists()):
        return None

    created_at = int(meta_file.read_text())
    now = int(time.time())

    if now - created_at > expiry_seconds:
        print(f"[⏳] Cache expired for key: {hash_key}")
        return None

    return cache_file.read_text()


import time

def cache_set(hash_key: str, value: str):
    # Save data
    cache_file = CACHE_DIR / f"{hash_key}.txt"
    cache_file.write_text(value)

    # Save metadata
    meta_file = CACHE_DIR / f"{hash_key}.meta"
    meta_file.write_text(str(int(time.time())))


def cached_call(text: str, call_fn) -> str:
    key = hash_text(text)
    cached = cache_get(key)
    if cached is not None:
        print(f"[⚡] Cache hit: {key}")
        return cached
    print(f"[🧠] Cache miss: {key}")
    result = call_fn(text)
    cache_set(key, result)
    return result
