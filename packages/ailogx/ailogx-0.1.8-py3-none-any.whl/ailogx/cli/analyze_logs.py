# llm_logger/cli/analyze_logs.py
import argparse
from llm_logger.analyzers.groq_analyzer import GroqAnalyzer
from llm_logger.analyzers.ollama_analyzer import OllamaAnalyzer
from llm_logger.analyzers.openai_analyzer import OpenAIAnalyzer
from llm_logger.formatters.structured import to_llm_format
from llm_logger.utils import load_jsonl

def get_analyzer(engine):
    if engine == "groq":
        return GroqAnalyzer()
    elif engine == "ollama":
        return OllamaAnalyzer()
    elif engine == "openai":
        return OpenAIAnalyzer()
    raise ValueError("Unsupported engine")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logfile", required=True)
    parser.add_argument("--engine", choices=["groq", "ollama", "openai"], required=True)
    parser.add_argument("--prompt", default="Summarize the behavior, decisions, and errors from this log.")
    args = parser.parse_args()

    logs = load_jsonl(args.logfile)
    text = to_llm_format(logs[:1000])
    analyzer = get_analyzer(args.engine)

    print("\n===== LLM Summary =====")
    print(analyzer.analyze(text, args.prompt))
