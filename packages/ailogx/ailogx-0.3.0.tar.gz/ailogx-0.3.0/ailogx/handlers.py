# llm_logger/handlers.py
import logging
from .core import LLMLogger

class LLMLogHandler(logging.Handler):
    def __init__(self, llm_logger=None):
        super().__init__()
        self.llm_logger = llm_logger or LLMLogger("llm_bridge")

    def emit(self, record):
        msg = self.format(record)
        level = record.levelname.lower()

        if level == "error":
            self.llm_logger.llm_error(msg)
        elif level == "warning":
            self.llm_logger.llm_decision(msg)
        elif level == "info":
            self.llm_logger.llm_context(msg)
        else:
            self.llm_logger.llm_info(msg)
