import re
from collections import defaultdict

def smart_filter(logs):
    return [
        log for log in logs
        if log.get("level") in {
            "error_reasoning", "function_exit_error", "decision_point"
        } or log.get("reason") or log.get("summary")
    ]

def intent_filter(logs, intent):
    intent_keywords = intent.lower().split()
    def matches(log):
        text = f"{log.get('message', '')} {log.get('reason', '')}".lower()
        return all(word in text for word in intent_keywords)

    return [log for log in logs if matches(log)]

def fast_mode(logs):
    groups = defaultdict(list)
    for log in logs:
        group = log.get("context_id") or log.get("file") or "global"
        groups[group].append(log)

    result = []
    for g, entries in groups.items():
        if len(entries) > 20:
            result.append(entries[len(entries) // 2])  # take a middle log
        else:
            result.extend(entries)
    return result
