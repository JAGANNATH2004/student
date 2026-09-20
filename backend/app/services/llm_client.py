"""
Pluggable LLM client (Module 6 / RAG generation step).
LLM_PROVIDER=openai  -> uses OpenAI Chat Completions API
LLM_PROVIDER=ollama  -> uses a local Ollama server (free, runs on your machine)
Switch providers purely via .env — no code changes needed.
"""
import requests
from app.config import settings


def _chat_openai(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content or ""


def _chat_ollama(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    url = f"{settings.OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": temperature},
    }
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json().get("message", {}).get("content", "")


def chat_completion(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    if settings.LLM_PROVIDER == "ollama":
        return _chat_ollama(system_prompt, user_prompt, temperature)
    return _chat_openai(system_prompt, user_prompt, temperature)
