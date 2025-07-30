# llm_logger/backends/registry.py

import os

def get_analyzer():
    backend = os.environ.get("LLM_LOGGER_BACKEND", "ollama").lower()

    if backend == "groq":
        from llm_logger.backends import groq
        return groq.analyze
    elif backend == "openai":
        from llm_logger.backends import openai
        return openai.analyze
    elif backend == "ollama":
        from llm_logger.backends import ollama
        return ollama.analyze
    else:
        raise ValueError(f"Unsupported LLM backend: {backend}")
