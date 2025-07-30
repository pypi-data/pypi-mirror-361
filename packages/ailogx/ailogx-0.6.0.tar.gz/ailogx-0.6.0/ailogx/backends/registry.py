# ailogx/backends/registry.py

import os

def get_analyzer():
    backend = os.environ.get("LLM_LOGGER_BACKEND", "ollama").lower()

    if backend == "groq":
        from ailogx.backends import groq
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return lambda text: groq.analyze(text, model=model)

    elif backend == "openai":
        from ailogx.backends import openai
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
        return lambda text: openai.analyze(text, model=model)

    elif backend == "ollama":
        from ailogx.backends import ollama
        model = os.getenv("OLLAMA_MODEL", "llama3")
        return lambda text: ollama.analyze(text, model=model)

    else:
        raise ValueError(f"Unsupported LLM backend: {backend}")
