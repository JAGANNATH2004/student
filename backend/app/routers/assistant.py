"""Module 6 — AI Learning Assistant using RAG (the flagship feature)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, get_current_user
from app.services.rag_engine import answer_question

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])


@router.post("/ask", response_model=schemas.AssistantAnswer)
def ask(
    payload: schemas.AssistantQuery,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = answer_question(payload.course_id, payload.question)

    db.add(models.ChatMessage(
        user_id=current_user.id, course_id=payload.course_id,
        role="user", content=payload.question,
    ))
    db.add(models.ChatMessage(
        user_id=current_user.id, course_id=payload.course_id,
        role="assistant", content=result["answer"],
        sources=result["sources"], confidence=result["confidence"],
    ))
    if payload.course_id:
        db.add(models.LearningActivityLog(
            student_id=current_user.id, course_id=payload.course_id,
            activity_type="chat_query",
        ))
    db.commit()

    return schemas.AssistantAnswer(**result)


@router.get("/history")
def history(
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.ChatMessage).filter(models.ChatMessage.user_id == current_user.id)
    if course_id:
        q = q.filter(models.ChatMessage.course_id == course_id)
    messages = q.order_by(models.ChatMessage.created_at.asc()).all()
    return [
        {
            "role": m.role, "content": m.content, "sources": m.sources,
            "confidence": m.confidence, "created_at": m.created_at,
        }
        for m in messages
    ]
