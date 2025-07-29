# llm_logger/decorators.py
from functools import wraps
import inspect
from .core import LLMLogger

llmlogger = LLMLogger("decorated")

def llm_logged(reason=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            inputs = dict(zip(inspect.signature(func).parameters, args))
            inputs.update(kwargs)
            with llmlogger.function_span(func.__name__, reason=reason):
                try:
                    output = func(*args, **kwargs)
                    llmlogger.llm_info(f"{func.__name__} returned", outputs=output)
                    return output
                except Exception as e:
                    llmlogger.llm_error(f"{func.__name__} raised exception", reason=str(e))
                    raise
        return wrapper
    return decorator
