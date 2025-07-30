import re
import json
from collections import defaultdict

def smart_filter(logs):
    """
    Keep only logs that are useful for reasoning and summarization.
    Prioritizes logs with semantic weight (e.g., decisions, errors, reasons).
    """
    return [
        log for log in logs
        if log.get("level") in {
            "error_reasoning", "function_exit_error", "decision_point",
            "error", "critical"
        } or log.get("reason") or log.get("summary")
    ]


def intent_filter(logs, intent_string):
    """
    Naive keyword matching for user-defined intent string (e.g. "focus on auth errors").
    If no logs match, fallback to original logs and emit warning.
    """
    keywords = re.findall(r"\w+", intent_string.lower())

    def matches_intent(log):
        try:
            text = json.dumps(log).lower()
            return any(kw in text for kw in keywords)
        except Exception:
            return False  # skip logs that can't be serialized

    filtered = [log for log in logs if matches_intent(log)]

    if not filtered:
        print("⚠️  No logs matched intent keywords, returning original logs.")
        return logs

    return filtered


def fast_mode(logs, threshold=20):
    """
    Downsample logs for performance by selecting 1 representative log per group
    if group is too large. Keeps smaller groups intact.
    """
    groups = defaultdict(list)
    for log in logs:
        group = (
            log.get("context_id")
            or log.get("group_id")
            or log.get("file")
            or "global"
        )
        groups[group].append(log)

    result = []
    for group_id, entries in groups.items():
        if len(entries) > threshold:
            mid = len(entries) // 2
            result.append(entries[mid])
        else:
            result.extend(entries)

    return result
