"""Module 9 — Learning Analytics Dashboard (admin/faculty course + engagement view)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models
from app.deps import get_db, require_roles

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("admin", "faculty")),
):
    total_students = db.query(models.User).filter(models.User.role == models.UserRole.student).count()
    total_courses = db.query(models.Course).count()
    total_materials = db.query(models.Material).count()
    total_enrollments = db.query(models.Enrollment).count()

    course_stats = (
        db.query(
            models.Course.id, models.Course.title,
            func.count(models.Enrollment.id).label("enrollment_count"),
        )
        .outerjoin(models.Enrollment, models.Enrollment.course_id == models.Course.id)
        .group_by(models.Course.id)
        .all()
    )

    quiz_avg = db.query(func.avg(models.QuizAttempt.score_percent)).scalar() or 0.0

    return {
        "total_students": total_students,
        "total_courses": total_courses,
        "total_materials": total_materials,
        "total_enrollments": total_enrollments,
        "average_quiz_score": round(float(quiz_avg), 1),
        "course_engagement": [
            {"course_id": c.id, "title": c.title, "enrollment_count": c.enrollment_count}
            for c in course_stats
        ],
    }
