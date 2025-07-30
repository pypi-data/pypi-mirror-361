# llm_logger/backends/registry.py

import os

def get_analyzer():
    backend = os.environ.get("LLM_LOGGER_BACKEND", "ollama").lower()

    if backend == "groq":
        from ailogx.backends import groq
        return groq.analyze
    elif backend == "openai":
        from ailogx.backends import openai
        return openai.analyze
    elif backend == "ollama":
        from ailogx.backends import ollama
        return ollama.analyze
    else:
        raise ValueError(f"Unsupported LLM backend: {backend}")
