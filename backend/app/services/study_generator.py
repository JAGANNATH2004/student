"""
AI Study Material Generator (Module 4): summaries, flashcards, quizzes and
revision notes, generated from a material's extracted text via the LLM.
Prompts explicitly request STRICT JSON so the API can parse structured
output reliably instead of scraping free text.
"""
import json
import re
from typing import Any, Dict, List

from app.services.llm_client import chat_completion

SYSTEM_PROMPT = (
    "You are an expert instructional designer creating study aids for "
    "university students. Always respond with STRICT, VALID JSON matching "
    "exactly the schema requested — no markdown fences, no commentary."
)


def _extract_json(raw: str) -> Any:
    raw = raw.strip()
    raw = re.sub(r"^```json|^```|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise


def generate_summary(text: str, max_words: int = 250) -> str:
    prompt = (
        f"Summarize the following course material in about {max_words} words, "
        f"focused on key concepts a student must remember:\n\n{text[:6000]}"
    )
    return chat_completion(
        "You are an expert instructional designer. Write a clear, well-structured summary.",
        prompt,
    )


def generate_flashcards(text: str, num_items: int = 8) -> List[Dict[str, str]]:
    prompt = (
        f"From the material below, create exactly {num_items} flashcards as a JSON array "
        f'of objects: [{{"question": "...", "answer": "..."}}].\n\nMATERIAL:\n{text[:6000]}'
    )
    raw = chat_completion(SYSTEM_PROMPT, prompt)
    return _extract_json(raw)


def generate_quiz(text: str, num_items: int = 5) -> List[Dict[str, Any]]:
    prompt = (
        f"From the material below, create exactly {num_items} multiple-choice questions as a "
        f'JSON array: [{{"question": "...", "options": ["A","B","C","D"], '
        f'"answer_index": 0, "explanation": "..."}}]. Exactly one correct option per question.'
        f"\n\nMATERIAL:\n{text[:6000]}"
    )
    raw = chat_completion(SYSTEM_PROMPT, prompt)
    return _extract_json(raw)


def generate_revision_notes(text: str) -> str:
    prompt = (
        "Turn the following material into concise bullet-point revision notes, "
        f"grouped under short headings:\n\n{text[:6000]}"
    )
    return chat_completion(
        "You are an expert instructional designer. Produce well-organized bullet notes.",
        prompt,
    )
