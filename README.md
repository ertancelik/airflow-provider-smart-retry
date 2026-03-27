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

