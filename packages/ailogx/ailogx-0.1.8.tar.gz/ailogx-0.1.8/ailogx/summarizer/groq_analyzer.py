# llm_logger/summarizer/groq_analyzer.py

import asyncio
from groq import Groq
import os

class GroqAnalyzer:
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self.client = Groq(
                api_key=os.environ.get("GROQ_API_KEY"),
                )
        self.model = model

    def _analyze_async(self, text: str, prompt: str = "Summarize the following logs:") -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content.strip()

    def analyze(self, text: str, prompt: str = "Summarize the following logs:") -> str:
        return self._analyze_async(text, prompt)
