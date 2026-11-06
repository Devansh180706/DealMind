"""
Reliable LLM wrapper around Groq API.
Features:
- Exponential backoff retry on transient API errors.
- Strict JSON schema validation using Pydantic.
- Re-prompting the model with parser errors up to 3 times.
- Safe fallback when all parsing attempts fail.
"""

import os
import time
import json
import logging
from typing import Type, TypeVar, Optional, Any, Union
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("agent.llm")

T = TypeVar("T", bound=BaseModel)

# Default models
PRIMARY_MODEL = os.getenv("GROQ_PRIMARY_MODEL", "openai/gpt-oss-120b")
FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "qwen/qwen3.8-27b")


class LLMClient:
    """Wrapper around Groq API with robust retry, backoff, and JSON repair."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment or constructor.")
        
        from groq import Groq
        self.client = Groq(api_key=self.api_key)

    def chat(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        max_retries: int = 3,
    ) -> str:
        """Execute a text chat completion with exponential backoff retry."""
        selected_model = model or PRIMARY_MODEL
        delay = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=selected_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                choice = response.choices[0]
                content = choice.message.content or ""
                return content.strip()
            except Exception as e:
                logger.warning(
                    f"Groq API call attempt {attempt}/{max_retries} failed with {selected_model}: {e}"
                )
                if attempt == max_retries:
                    # Try falling back to alternative model once if primary failed
                    if selected_model != FALLBACK_MODEL:
                        logger.info(f"Retrying with fallback model: {FALLBACK_MODEL}")
                        try:
                            fallback_resp = self.client.chat.completions.create(
                                model=FALLBACK_MODEL,
                                messages=messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                            )
                            return (fallback_resp.choices[0].message.content or "").strip()
                        except Exception as fallback_err:
                            logger.error(f"Fallback model also failed: {fallback_err}")
                    raise RuntimeError(f"All Groq completion attempts failed: {e}") from e
                
                time.sleep(delay)
                delay *= 2.0

        return ""

    def chat_json(
        self,
        messages: list[dict[str, str]],
        schema: Type[T],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_repairs: int = 3,
    ) -> T:
        """
        Execute completion with strict Pydantic JSON validation.
        If output is malformed or invalid JSON, re-prompts the model with the error up to 3 times.
        """
        json_prompt = (
            f"\n\nCRITICAL: Respond ONLY with a valid JSON object matching this schema:\n"
            f"{json.dumps(schema.model_json_schema(), indent=2)}\n"
            "Do not include markdown codeblocks (no ```json), do not include commentary."
        )

        # Clone messages and augment system/user prompt
        working_messages = [dict(m) for m in messages]
        working_messages[-1]["content"] += json_prompt

        last_error = ""
        last_raw_output = ""

        for repair_attempt in range(1, max_repairs + 1):
            raw_text = self.chat(
                messages=working_messages,
                model=model,
                temperature=temperature,
            )
            last_raw_output = raw_text

            # Clean markdown wrappers if model still included them
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            try:
                parsed_dict = json.loads(clean_text)
                validated_obj = schema.model_validate(parsed_dict)
                return validated_obj
            except (json.JSONDecodeError, ValidationError) as err:
                last_error = str(err)
                logger.warning(
                    f"JSON validation attempt {repair_attempt}/{max_repairs} failed: {err}\nRaw output: {raw_text[:200]}"
                )
                if repair_attempt < max_repairs:
                    # Append assistant bad output and prompt with repair instruction
                    working_messages.append({"role": "assistant", "content": raw_text})
                    working_messages.append({
                        "role": "user",
                        "content": (
                            f"Your previous response caused validation error:\n{last_error}\n\n"
                            f"Please fix the error and output ONLY the corrected JSON object matching the schema."
                        )
                    })

        # Graceful fallback: attempt partial parse or raise structured error
        raise ValueError(
            f"Failed to obtain valid JSON matching {schema.__name__} after {max_repairs} attempts. "
            f"Last error: {last_error}. Last raw output: {last_raw_output}"
        )


# Global singleton instance
_llm_instance: Optional[LLMClient] = None

def get_llm() -> LLMClient:
    """Return initialized singleton LLMClient."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMClient()
    return _llm_instance
