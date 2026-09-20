"""Module 7 & 8 — Explainable Learning Analytics + Personalized Learning Path."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, get_current_user, require_roles
from app.services.analytics_engine import analyze_student, generate_learning_path

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/course/{course_id}", response_model=schemas.AnalyticsOut)
def my_analytics(
    course_id: int, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return analyze_student(db, current_user.id, course_id)


@router.get("/course/{course_id}/student/{student_id}", response_model=schemas.AnalyticsOut)
def student_analytics_for_faculty(
    course_id: int, student_id: int, db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("faculty", "admin")),
):
    return analyze_student(db, student_id, course_id)


@router.get("/course/{course_id}/learning-path", response_model=schemas.LearningPathOut)
def my_learning_path(
    course_id: int, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    steps = generate_learning_path(db, current_user.id, course_id)
    db.add(models.LearningPath(student_id=current_user.id, course_id=course_id, steps=steps))
    db.commit()
    return schemas.LearningPathOut(steps=steps)
