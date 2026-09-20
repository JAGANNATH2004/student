"""Module 4 — AI Study Material Generator: summaries/flashcards/quizzes/notes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, require_roles, get_current_user
from app.services.study_generator import (
    generate_summary, generate_flashcards, generate_quiz, generate_revision_notes,
)

router = APIRouter(prefix="/api/study", tags=["Study Material Generator"])


@router.post("/generate")
def generate(
    payload: schemas.GenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    material = db.query(models.Material).get(payload.material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if not material.raw_text:
        raise HTTPException(status_code=400, detail="Material has not finished processing yet")

    if payload.kind == "summary":
        return {"kind": "summary", "content": generate_summary(material.raw_text)}
    elif payload.kind == "flashcards":
        return {"kind": "flashcards", "content": generate_flashcards(material.raw_text, payload.num_items)}
    elif payload.kind == "revision_notes":
        return {"kind": "revision_notes", "content": generate_revision_notes(material.raw_text)}
    elif payload.kind == "quiz":
        questions = generate_quiz(material.raw_text, payload.num_items)
        quiz = models.Quiz(
            course_id=material.course_id, title=f"Quiz: {material.title}",
            source_material_id=material.id, questions=questions,
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        return {"kind": "quiz", "quiz_id": quiz.id, "content": questions}
    else:
        raise HTTPException(status_code=400, detail="kind must be one of: summary, flashcards, quiz, revision_notes")


@router.get("/quizzes/course/{course_id}")
def list_quizzes(course_id: int, db: Session = Depends(get_db)):
    quizzes = db.query(models.Quiz).filter(models.Quiz.course_id == course_id).all()
    return [{"id": q.id, "title": q.title, "num_questions": len(q.questions)} for q in quizzes]


@router.get("/quizzes/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(models.Quiz).get(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"id": quiz.id, "title": quiz.title, "questions": quiz.questions}


@router.post("/quizzes/submit", response_model=schemas.QuizResult)
def submit_quiz(
    payload: schemas.QuizSubmit,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("student")),
):
    quiz = db.query(models.Quiz).get(payload.quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = quiz.questions
    correct = 0
    review = []
    for i, q in enumerate(questions):
        selected = payload.answers[i] if i < len(payload.answers) else None
        is_correct = selected == q["answer_index"]
        if is_correct:
            correct += 1
        review.append({
            "question": q["question"], "selected": selected,
            "correct_index": q["answer_index"], "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    score_percent = round((correct / len(questions)) * 100, 1) if questions else 0.0

    attempt = models.QuizAttempt(
        quiz_id=quiz.id, student_id=current_user.id,
        answers=payload.answers, score_percent=score_percent,
    )
    db.add(attempt)
    db.add(models.LearningActivityLog(
        student_id=current_user.id, course_id=quiz.course_id, activity_type="quiz_attempt",
    ))
    db.commit()

    return schemas.QuizResult(
        score_percent=score_percent, correct_count=correct, total=len(questions), review=review,
    )
