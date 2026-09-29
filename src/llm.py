"""Thin wrapper around the language model. You should not need to change this file.

Two functions:
    ask_json(prompt, schema, system=None) -> (parsed, raw_text)
    ask_text(prompt, system=None)         -> raw_text

Configuration (environment variables):
    LLM_BACKEND   "ollama" (default) or "gemini" (fallback, see the setup guide)
    LLM_MODEL     Ollama model name, default "qwen2.5:3b" - everyone uses the same model
    GEMINI_MODEL  required for the gemini backend: copy the model name from Google AI Studio
    LLM_NUM_CTX     Ollama context window in tokens, default 8192
    LLM_MAX_TOKENS  maximum tokens the model may generate per call, default 2048
    LLM_TIMEOUT     seconds to wait for one answer, default 300
    LLM_VERBOSE     set to 1 to print the model's output live while it is generated

STATS counts calls and time; run.py resets and records it for every run.
"""
import json
import os
import re
import sys
import time
from typing import Optional, Type, Union

from pydantic import BaseModel, ValidationError

BACKEND = os.environ.get("LLM_BACKEND", "ollama")
MODEL = os.environ.get("LLM_MODEL", "qwen2.5:3b")
NUM_CTX = int(os.environ.get("LLM_NUM_CTX", "8192"))
MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "2048"))
TIMEOUT = float(os.environ.get("LLM_TIMEOUT", "300"))
VERBOSE = os.environ.get("LLM_VERBOSE", "") not in ("", "0")
STATS = {"calls": 0, "seconds": 0.0}


class LLMError(Exception):
    """The model answered, but the answer is not valid for the requested schema."""

    def __init__(self, message: str, raw: str = ""):
        super().__init__(message)
        self.raw = raw


def reset_stats():
    STATS["calls"], STATS["seconds"] = 0, 0.0


def model_name() -> str:
    return MODEL if BACKEND == "ollama" else f"gemini:{os.environ.get('GEMINI_MODEL', '?')}"


def _strip_fences(text: str) -> str:
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    return m.group(1).strip() if m else text.strip()


def _call_ollama(prompt: str, system: Optional[str], schema: Optional[dict], temperature: float) -> str:
    import ollama
    client = ollama.Client(timeout=TIMEOUT)
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    kwargs = {"options": {"temperature": temperature, "num_ctx": NUM_CTX, "num_predict": MAX_TOKENS}}
    if schema is not None:
        kwargs["format"] = schema                  # Ollama constrains the output to this JSON schema
    try:
        if VERBOSE:                                # stream tokens to the terminal as they are generated
            parts, done_reason = [], None
            sys.stderr.write("\n----- model output -----\n")
            for chunk in client.chat(model=MODEL, messages=messages, stream=True, **kwargs):
                piece = chunk.message.content or ""
                parts.append(piece)
                sys.stderr.write(piece)
                sys.stderr.flush()
                if getattr(chunk, "done", False):
                    done_reason = getattr(chunk, "done_reason", None)
            sys.stderr.write("\n----- end of model output -----\n")
            text = "".join(parts)
        else:
            resp = client.chat(model=MODEL, messages=messages, **kwargs)
            text, done_reason = resp.message.content, getattr(resp, "done_reason", None)
    except Exception as e:  # noqa: BLE001
        if "timeout" in type(e).__name__.lower():
            raise LLMError(f"no answer from the model within {TIMEOUT:.0f} s (raise LLM_TIMEOUT to wait longer)") from e
        raise
    if done_reason == "length":
        raise LLMError(f"the model hit the {MAX_TOKENS}-token limit before finishing its answer "
                       f"(it may be looping; see raw_model_output)", text)
    return text


def _call(prompt: str, system: Optional[str], schema: Optional[dict], temperature: float) -> str:
    t0 = time.time()
    try:
        if BACKEND == "ollama":
            return _call_ollama(prompt, system, schema, temperature)
        if BACKEND == "gemini":
            gm = os.environ.get("GEMINI_MODEL")
            if not gm:
                raise RuntimeError("Set GEMINI_MODEL to a model name listed in Google AI Studio.")
            try:
                from google import genai
            except ImportError as e:
                raise RuntimeError("The gemini backend needs the client library: pip install google-genai") from e
            client = genai.Client()                # reads GEMINI_API_KEY from the environment
            config = {"temperature": temperature}
            if system:
                config["system_instruction"] = system
            if schema is not None:
                config["response_mime_type"] = "application/json"
            resp = client.models.generate_content(model=gm, contents=prompt, config=config)
            return resp.text
        raise RuntimeError(f"Unknown LLM_BACKEND: {BACKEND}")
    finally:
        STATS["calls"] += 1
        STATS["seconds"] += time.time() - t0


def ask_text(prompt: str, system: Optional[str] = None, temperature: float = 0.0) -> str:
    """Free-text answer."""
    return _call(prompt, system, None, temperature)


def ask_json(prompt: str, schema: Union[Type[BaseModel], dict], system: Optional[str] = None,
             temperature: float = 0.0):
    """JSON answer constrained to `schema` (a Pydantic model class or a JSON-schema dict).

    Returns (parsed, raw_text). `parsed` is a model instance if `schema` is a Pydantic class, else a dict.
    Raises LLMError if the output cannot be parsed or validated - catch it if you want to retry.
    """
    is_model = isinstance(schema, type) and issubclass(schema, BaseModel)
    json_schema = schema.model_json_schema() if is_model else schema
    raw = _call(prompt, system, json_schema, temperature)
    text = _strip_fences(raw)
    try:
        return (schema.model_validate_json(text) if is_model else json.loads(text)), raw
    except (ValidationError, json.JSONDecodeError) as e:
        raise LLMError(f"model output does not match the schema: {e}", raw) from e
