# llm_logger/summarizer/chunker.py

from typing import List, Dict, Generator

def chunk_logs(logs: List[Dict], chunk_size: int = 500) -> Generator[List[Dict], None, None]:
    """
    Yield fixed-size chunks from a list of logs.
    """
    for i in range(0, len(logs), chunk_size):
        yield logs[i:i + chunk_size]


def score_log(log: Dict) -> int:
    """
    Assign a score to a log entry based on its importance.
    Higher score = more LLM-worthy.
    """
    level = log.get("level", "").lower()
    if "error" in level:
        return 5
    if "decision" in level:
        return 4
    if "function_exit_error" in level:
        return 4
    if "function_exit" in level or "context_info" in level:
        return 2
    return 1


def score_chunk(chunk: List[Dict]) -> int:
    return sum(score_log(log) for log in chunk)


def prioritize_chunks(
    logs: List[Dict],
    chunk_size: int = 500,
    top_k: int = 20
) -> List[List[Dict]]:
    """
    Returns the top_k chunks with highest importance scores.
    """
    chunks = list(chunk_logs(logs, chunk_size))
    scored = [(score_chunk(c), c) for c in chunks]
    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for _, c in scored[:top_k]]
