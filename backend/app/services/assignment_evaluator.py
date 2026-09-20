"""
AI-Based Assignment Evaluation (Module 7, optional per spec). Gives
preliminary feedback on descriptive answers across four rubric dimensions.
This is explicitly framed to students/instructors as PRELIMINARY, non-final
feedback — the instructor still grades officially.
"""
import json
import re
from typing import Dict, Any

from app.services.llm_client import chat_completion

SYSTEM_PROMPT = (
    "You are a fair, constructive teaching assistant giving PRELIMINARY "
    "feedback on a student's written answer. Respond with STRICT JSON only."
)


def evaluate_submission(instructions: str, answer_text: str) -> Dict[str, Any]:
    prompt = (
        f"Assignment instructions:\n{instructions}\n\n"
        f"Student answer:\n{answer_text}\n\n"
        "Score the answer from 0-100 on each of: relevance, completeness, "
        "writing_quality, concept_coverage. Then give 3-5 sentences of "
        "constructive feedback. Respond as JSON:\n"
        '{"relevance": 0-100, "completeness": 0-100, "writing_quality": 0-100, '
        '"concept_coverage": 0-100, "feedback": "..."}'
    )
    raw = chat_completion(SYSTEM_PROMPT, prompt)
    raw = re.sub(r"^```json|^```|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group(0)) if match else {
            "relevance": 50, "completeness": 50, "writing_quality": 50,
            "concept_coverage": 50, "feedback": "Automated evaluation unavailable; please review manually.",
        }
