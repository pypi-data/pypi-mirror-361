# llm_logger/summarizer/summarizer.py

from typing import List, Dict, Callable
from ailogx.summarizer.chunker import prioritize_chunks
from ailogx.summarizer.cache import cached_call

def default_formatter(chunk: List[Dict]) -> str:
    lines = []
    for log in chunk:
        timestamp = log.get("timestamp", "")
        level = log.get("level", "").upper()
        msg = log.get("message", "")
        reason = log.get("reason", "")
        inputs = log.get("inputs", "")
        outputs = log.get("outputs", "")
        lines.append(f"[{timestamp}] {level}: {msg}")
        if reason:
            lines.append(f"↳ REASON: {reason}")
        if inputs:
            lines.append(f"↳ INPUTS: {inputs}")
        if outputs:
            lines.append(f"↳ OUTPUTS: {outputs}")
    return "\n".join(lines)


def multi_pass_summarize(
    logs: List[Dict],
    analyzer: Callable[[str], str],
    chunk_size: int = 500,
    top_k: int = 20,
    formatter: Callable[[List[Dict]], str] = default_formatter
) -> str:
    """
    Summarize logs in multiple passes using an LLM analyzer.
    """
    top_chunks = prioritize_chunks(logs, chunk_size=chunk_size, top_k=top_k)
    summaries = []

    for chunk in top_chunks:
        text = formatter(chunk)
        text = text.strip().replace("\r\n", "\n")
        summary = cached_call(text, analyzer)
        # summary = analyzer(text)
        summaries.append(summary)

    merged = "\n\n".join(summaries)
    # final_summary = analyzer(merged)
    final_summary = cached_call(merged, analyzer)  # ✅ Cache this too

    return final_summary
