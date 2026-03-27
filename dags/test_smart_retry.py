import random
from datetime import datetime
from airflow import DAG
from smart_retry.operator import LLMSmartRetryOperator

def flaky_task(context):
    r = random.random()
    if r < 0.4:
        raise ConnectionError("Network timeout: connection refused after 30s")
    elif r < 0.7:
        raise Exception("429 Too Many Requests: rate limit exceeded")
    return "Success!"

with DAG(
    dag_id="test_smart_retry",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    smart_task = LLMSmartRetryOperator(
        task_id="smart_retry_task",
        task_callable=flaky_task,
        max_retries=3,
    )