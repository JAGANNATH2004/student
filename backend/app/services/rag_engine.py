"""
Retrieval-Augmented Generation engine (Module 1 & Module 6 — the core
"AI Learning Assistant" feature). Instead of answering purely from an LLM's
parametric memory, it:
  1. Retrieves the most relevant chunks from the course's vector store
  2. Builds a grounded prompt (context + question)
  3. Asks the LLM to answer ONLY using that context
  4. Returns the answer plus source attribution + a confidence score
     (Module 8: Explainable AI)
"""
from typing import Optional, Dict, Any, List

from app.services.vector_store import semantic_search
from app.services.llm_client import chat_completion

SYSTEM_PROMPT = (
    "You are an AI Learning Assistant for a university e-learning platform. "
    "Answer the student's question using ONLY the provided course context. "
    "If the context does not contain enough information, say so honestly and "
    "give the best general guidance you can, clearly flagged as not sourced "
    "from course material. Be clear, concise, and educational."
)


def answer_question(course_id: Optional[int], question: str, top_k: int = 5) -> Dict[str, Any]:
    if course_id is None:
        # No course scope -> no retrieval possible, answer generally with low confidence.
        answer = chat_completion(SYSTEM_PROMPT, question)
        return {"answer": answer, "sources": [], "confidence": 0.35}

    retrieved: List[Dict[str, Any]] = semantic_search(course_id, question, top_k=top_k)

    if not retrieved:
        answer = chat_completion(
            SYSTEM_PROMPT,
            f"No course material has been indexed yet for this course. "
            f"Answer generally, but tell the student no course-specific "
            f"sources were found.\n\nQuestion: {question}",
        )
        return {"answer": answer, "sources": [], "confidence": 0.3}

    context_block = "\n\n---\n\n".join(
        f"[Source: {r['material_title']}]\n{r['chunk_text']}" for r in retrieved
    )
    user_prompt = (
        f"COURSE CONTEXT:\n{context_block}\n\n"
        f"STUDENT QUESTION:\n{question}\n\n"
        f"Answer using the context above. Mention which source(s) informed your answer."
    )
    answer = chat_completion(SYSTEM_PROMPT, user_prompt)

    # Confidence = average retrieval similarity, a simple but honest proxy —
    # displayed to the user rather than a black-box number (Explainable AI).
    avg_score = sum(r["score"] for r in retrieved) / len(retrieved)
    sources = [
        {
            "material_id": r["material_id"],
            "title": r["material_title"],
            "snippet": r["chunk_text"][:220] + ("..." if len(r["chunk_text"]) > 220 else ""),
            "relevance": r["score"],
        }
        for r in retrieved
    ]
    return {"answer": answer, "sources": sources, "confidence": round(avg_score, 2)}
