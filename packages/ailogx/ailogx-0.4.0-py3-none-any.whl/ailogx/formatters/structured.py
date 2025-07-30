# llm_logger/formatters/structured.py
def to_llm_format(logs: list[dict]) -> str:
    return "\n".join(
        f"[{log['timestamp']}][{log['level']}][{log['function']}]: {log['message']}"
        for log in logs
    )
