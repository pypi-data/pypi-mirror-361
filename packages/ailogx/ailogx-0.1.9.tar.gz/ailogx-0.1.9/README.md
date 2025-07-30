# 🧠 LLM Logger

**LLM Logger** is a Python logging framework designed for seamless integration with **Large Language Models (LLMs)**.  
It produces structured, LLM-friendly logs that can be easily summarized or reasoned about — even across massive, deeply nested codebases.

---

## 🚀 Features

- 🪵 **Structured JSON logs** (timestamped, contextual, machine-readable)
- 🧠 **LLM-optimized format** with `reason`, `inputs`, `outputs`, and semantic tags
- 📂 **Log grouping** (`start_group`, `end_group`) and function spans
- 🔌 **Modular LLM backend** support via environment variable:
  - `Ollama` (local models)
  - `Groq` (LLama, Gemma via API)
  - `OpenAI` (GPT-3.5 / GPT-4)
- 📊 **Summarization CLI** with smart filtering and token-aware chunking
- 💾 **Cache** for LLM calls with expiration/cleanup
- 🧪 **Test harness** to simulate deeply nested logs

---

## 📦 Installation

```bash
pip install ailogx
```

## 🛠️ Basic Usage

```python
from ailogx.core import LLMLogger

log = LLMLogger("my-service")

log.llm_info("User login started", inputs={"username": "admin"})
log.llm_decision("Using 2FA", reason="high-risk user")
log.llm_error("Login failed", reason="Invalid OTP")
```

## 🔁 Function Span

```python
with log.function_span("process_payment", reason="checkout flow"):
    # your logic
    pass
```

## 📂 Grouping Logs

```python
log.start_group("req-42", reason="incoming API request")
# your logs here
log.end_group("req-42")
```

## 📊 LLM Summarization

### 🧠 Environment-based Backend Selection

Supports:

- `LLM_LOGGER_BACKEND=ollama` (default)
- `LLM_LOGGER_BACKEND=groq`
- `LLM_LOGGER_BACKEND=openai`

### 🧾 Example

```bash
export LLM_LOGGER_BACKEND=groq  # or 'openai', 'ollama'
export GROQ_API_KEY="your-groq-api-key"
- You must have a Groq account.
- Supported models: gemma3, llama3-70b, etc.

export OPENAI_API_KEY="your-openai-api-key"
- You must have an OpenAI API key.Models like gpt-3.5-turbo, gpt-4, etc. are supported.

llama (Local LLMs)
# Ollama must be running locally (default http://localhost:11434)
export OLLAMA_MODEL="llama3"
- No API key required.Make sure you have a local model pulled(ollama pull llama3).

python -m llm_logger.summarize simulated_logs/deep_nested_logs.jsonl --filter=smart --fast
```

Or call from Python:

```python
from ailogx.summarizer.summarizer import multi_pass_summarize
from ailogx.backends.registry import get_analyzer
import json

with open("llm_logs.jsonl") as f:
    logs = [json.loads(line) for line in f]

summary = multi_pass_summarize(logs, get_analyzer())
print(summary)
```

## 🧪 Test Harness

Generate deep, nested logs for benchmarking:

```bash
python ailogx/core.py
```

Outputs:

- `llm_simulated_logs.jsonl` (LLMLogger)
- `standard_simulated_logs.log` (Python logging)

## 🔁 Cache & Optimization

- ✅ LLM responses cached to `.cache/`
- 🧠 Token-aware chunking
- 🔎 Smart filtering (`--filter=smart`, `--intent="auth errors"`)
- ⚡ `--fast` mode for shallow summaries before full deep dives