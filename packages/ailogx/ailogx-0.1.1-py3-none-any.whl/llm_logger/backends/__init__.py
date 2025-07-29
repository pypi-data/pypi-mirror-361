import os

def get_analyzer():
    backend = os.getenv("LLM_LOGGER_BACKEND", "groq").lower()
    if backend == "groq":
        from .groq import analyze
    elif backend == "openai":
        from .openai import analyze
    elif backend == "ollama":
        from .ollama import analyze
    else:
        raise ValueError(f"Unsupported LLM_LOGGER_BACKEND: {backend}")
    return analyze
