# llm_logger/core.py
"""
LLM-Friendly Logging Library (Core Module)
"""
import json
import time
import uuid
import inspect
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

class LLMLogger:
    def __init__(self, name: str, log_path: str = "./llm_logs.jsonl"):
        self.name = name
        self.log_path = Path(log_path)
        self.context_id = str(uuid.uuid4())

        # Ensure log file exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.touch(exist_ok=True)

    def _get_caller_info(self):
        frame = inspect.currentframe()
        outer = inspect.getouterframes(frame)[3]  # 3 levels up
        return {
            "file": outer.filename,
            "line": outer.lineno,
            "function": outer.function
        }

    def _log(self, level: str, message: str, *, inputs=None, outputs=None, reason=None, summary=None):
        now = datetime.utcnow().isoformat() + "Z"
        caller_info = self._get_caller_info()

        log_entry = {
            "timestamp": now,
            "level": level,
            "logger": self.name,
            "message": message,
            "context_id": self.context_id,
            **caller_info
        }

        if inputs is not None:
            log_entry["inputs"] = inputs
        if outputs is not None:
            log_entry["outputs"] = outputs
        if reason is not None:
            log_entry["reason"] = reason
        if summary is not None:
            log_entry["summary"] = summary

        with open(self.log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def llm_info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def llm_decision(self, message: str, **kwargs):
        self._log("decision_point", message, **kwargs)

    def llm_error(self, message: str, **kwargs):
        self._log("error_reasoning", message, **kwargs)

    def llm_context(self, message: str, **kwargs):
        self._log("context_info", message, **kwargs)

    def llm_expected(self, message: str, **kwargs):
        self._log("expected_behavior", message, **kwargs)

    def start_group(self, name: str, reason: Optional[str] = None):
        self._log("group_start", f"Start group: {name}", reason=reason)

    def end_group(self, name: str):
        self._log("group_end", f"End group: {name}")

    def function_span(self, name: str, reason: Optional[str] = None):
        return _FunctionSpanLogger(self, name, reason)


class _FunctionSpanLogger:
    def __init__(self, logger: LLMLogger, name: str, reason: Optional[str] = None):
        self.logger = logger
        self.name = name
        self.reason = reason

    def __enter__(self):
        self.start_time = time.time()
        self.logger._log("function_entry", f"Entering function: {self.name}", reason=self.reason)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.time() - self.start_time
        message = f"Exiting function: {self.name} after {elapsed:.2f}s"
        if exc_type:
            self.logger._log("function_exit_error", message, reason=str(exc_value))
        else:
            self.logger._log("function_exit", message)


# === Test Harness Simulation ===
if __name__ == "__main__":
    import random

    logger = LLMLogger("test_harness", log_path="llm_simulated_logs.jsonl")
    logging.basicConfig(filename="standard_simulated_logs.log", level=logging.INFO)
    stdlog = logging.getLogger("standard")

    def simulate_layer(depth, max_depth):
        logger.llm_context(f"Entering layer {depth}", inputs={"depth": depth})
        stdlog.info(f"Entering layer {depth}")

        if depth < max_depth:
            for _ in range(random.randint(1, 3)):
                simulate_layer(depth + 1, max_depth)
        else:
            if random.random() < 0.3:
                logger.llm_error("Leaf operation failed", reason="simulated failure")
                stdlog.error("Leaf operation failed: simulated failure")
            else:
                logger.llm_info("Leaf operation succeeded")
                stdlog.info("Leaf operation succeeded")

        logger.llm_context(f"Exiting layer {depth}")
        stdlog.info(f"Exiting layer {depth}")

    def simulate_request(request_id):
        logger.start_group(f"request-{request_id}", reason="simulated user request")
        stdlog.info(f"Start request-{request_id}")
        simulate_layer(1, random.randint(4, 8))
        logger.end_group(f"request-{request_id}")
        stdlog.info(f"End request-{request_id}")

    for i in range(50):
        simulate_request(i)

    print("[✔] Test harness completed. Logs written to llm_simulated_logs.jsonl and standard_simulated_logs.log")