\# airflow-provider-smart-retry


An Apache Airflow provider that uses LLMs to make intelligent retry decisions when tasks fail.

[![PyPI version](https://badge.fury.io/py/airflow-provider-smart-retry.svg)](https://pypi.org/project/airflow-provider-smart-retry/)

## Installation
```bash
pip install airflow-provider-smart-retry
```

\## The Problem



Airflow's built-in retry mechanism is static — it waits the same amount of time and retries blindly regardless of the error type. This leads to:

\- Rate limit errors being retried too fast

\- Auth errors being retried pointlessly

\- Network errors not being retried fast enough



\## The Solution



`LLMSmartRetryOperator` analyzes the error log using a local LLM (via Ollama) and decides:

\- \*\*Should we retry at all?\*\* (auth errors → no)

\- \*\*How long should we wait?\*\* (rate limits → 60s, network → 0s)

\- \*\*What type of error is this?\*\* (rate\_limit / network / auth / data\_schema / unknown)



\## How It Works

Task Fails
↓
Extract full traceback
↓
Send to local Ollama LLM
↓
┌─────────────────────────────────────┐
│         Error Classification        │
│                                     │
│  rate_limit → wait 60s, retry 5x   │
│  network    → wait 15s, retry 4x   │
│  auth       → fail immediately ✗   │
│  data_schema→ fail immediately ✗   │
│  unknown    → wait 30s, retry 3x   │
└─────────────────────────────────────┘
↓
XCom’a classification bilgisi push edilir
↓
Airflow UI’dan izlenebilir



## Privacy & Security

All LLM inference runs **locally via Ollama**.  
Your error logs never leave your infrastructure. 🔒

Supported models: `llama3.2`, `mistral`, `phi3`, `gemma2`

