# llm_logger/utils.py
import json

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]
