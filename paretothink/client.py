"""Thin Bedrock **Converse** client: uniform text + token usage across model families.

Converse returns ``usage.inputTokens/outputTokens`` for every model (Llama, DeepSeek-R1,
Claude, Nova), which is exactly the provider-reported accounting the proof-slice needs
(DESIGN.md §10.5). Reasoning models emit a separate ``reasoningContent`` block; its tokens
are still counted in ``outputTokens`` (the over-think cost), while ``text`` holds the answer.
"""
from __future__ import annotations

import os

# macOS: the Objective-C runtime's fork/thread-safety guard segfaults boto3 when it is
# called from many threads (classic threaded-boto3 crash on Darwin). Disabling the guard
# is the standard workaround; the env var is a harmless no-op on Linux. Must be set before
# boto3 imports the SSL/Objective-C-linked libraries.
os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")

import random
import time
from dataclasses import dataclass

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

_RETRYABLE = {
    "ThrottlingException",
    "TooManyRequestsException",
    "ServiceUnavailableException",
    "ModelTimeoutException",
    "InternalServerException",
}


@dataclass
class Completion:
    text: str
    input_tokens: int
    output_tokens: int


class BedrockClient:
    """Minimal Converse wrapper with exponential backoff on throttling."""

    def __init__(self, model_id: str, region: str = "us-east-1", max_retries: int = 5):
        self.model_id = model_id
        self.max_retries = max_retries
        self._brt = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=Config(retries={"max_attempts": 1, "mode": "standard"}),
        )

    def complete(
        self, prompt: str, max_tokens: int = 512, temperature: float = 0.7
    ) -> Completion:
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                r = self._brt.converse(
                    modelId=self.model_id,
                    messages=[{"role": "user", "content": [{"text": prompt}]}],
                    inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
                )
                blocks = r["output"]["message"]["content"]
                text = "".join(b.get("text", "") for b in blocks)
                u = r["usage"]
                return Completion(text, u["inputTokens"], u["outputTokens"])
            except ClientError as e:
                code = e.response.get("Error", {}).get("Code", "")
                if code in _RETRYABLE and attempt < self.max_retries - 1:
                    last_err = e
                    time.sleep(2**attempt + random.random())  # backoff + jitter
                    continue
                raise
        assert last_err is not None
        raise last_err
