import time
import traceback
from airflow.sdk import BaseOperator
from smart_retry.llm_client import OllamaClient
from smart_retry.strategies import build_decision

class LLMSmartRetryOperator(BaseOperator):
    def __init__(
        self,
        task_callable,
        ollama_base_url: str = "http://host.docker.internal:11434",
        model: str = "llama3.1:8b",
        max_retries: int = 3,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.task_callable = task_callable
        self.ollama_base_url = ollama_base_url
        self.model = model
        self.max_retries = max_retries

    def execute(self, context):
        client = OllamaClient(base_url=self.ollama_base_url, model=self.model)
        attempt = 0

        while attempt <= self.max_retries:
            try:
                self.log.info(f"Attempt {attempt + 1}/{self.max_retries + 1}")
                return self.task_callable(context)

            except Exception as e:
                error_log = traceback.format_exc()
                self.log.error(f"Task failed:\n{error_log}")

                if attempt >= self.max_retries:
                    raise

                self.log.info("Asking LLM for retry strategy...")
                try:
                    decision = build_decision(client.classify_error(error_log))
                    self.log.info(
                        f"LLM Decision → type={decision.error_type}, "
                        f"retry={decision.should_retry}, "
                        f"wait={decision.wait_seconds}s | {decision.reason}"
                    )

                    if not decision.should_retry:
                        self.log.error("LLM says: do not retry. Failing task.")
                        raise

                    if decision.wait_seconds > 0:
                        self.log.info(f"Waiting {decision.wait_seconds} seconds...")
                        time.sleep(decision.wait_seconds)

                except Exception as llm_err:
                    self.log.warning(f"LLM unavailable, using default retry: {llm_err}")
                    time.sleep(30)

                attempt += 1