# orchestrator/app/llm/clients.py

import os
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, settings):
        backend = settings.LLM_BACKEND.lower()
        if backend == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.backend = "openai"

        elif backend == "llama":
            from transformers import pipeline
            self.client = pipeline(
                "text-generation",
                model=settings.LLAMA_MODEL_PATH,
                device="cpu"  # switch to "cuda" if you have a GPU
            )
            self.backend = "llama"

        else:
            raise ValueError(f"Unknown LLM_BACKEND: {settings.LLM_BACKEND!r}")

        logger.info("Initialized LLMClient with backend %r", self.backend)

    def generate(self, prompt: str, **kwargs) -> str:
        if self.backend == "openai":
            # Customize temperature, max_tokens, etc. via kwargs
            resp = self.client.chat.completions.create(
                model=kwargs.pop("model", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return resp.choices[0].message.content

        elif self.backend == "llama":
            # transformers pipeline returns a list of dicts
            out = self.client(prompt, **kwargs)
            return out[0].get("generated_text", "")

        else:
            # Should never happen
            raise RuntimeError(f"Unsupported backend {self.backend!r}")
