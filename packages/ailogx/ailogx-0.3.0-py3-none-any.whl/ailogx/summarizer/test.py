# test_summarizer.py

import json
from ailogx.summarizer.summarizer import multi_pass_summarize
from ailogx.summarizer.groq_analyzer import GroqAnalyzer

# Load logs from file
with open("llm_simulated_logs.jsonl") as f:
    logs = [json.loads(line) for line in f]

# Init Groq wrapper
analyzer = GroqAnalyzer(model="llama-3.1-8b-instant")

# Run summarizer
final = multi_pass_summarize(
    logs,
    analyzer=GroqAnalyzer().analyze,
    chunk_size=300,
    top_k=5
)


print("\n===== FINAL SUMMARY =====")
print(final)
