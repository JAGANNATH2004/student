"""Module 2 — Course & Content Management + enrollment."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, get_current_user, require_roles

router = APIRouter(prefix="/api/courses", tags=["Courses"])


@router.post("", response_model=schemas.CourseOut)
def create_course(
    payload: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("faculty", "admin")),
):
    if db.query(models.Course).filter(models.Course.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Course code already exists")
    course = models.Course(
        title=payload.title, code=payload.code, description=payload.description,
        instructor_id=current_user.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=List[schemas.CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).order_by(models.Course.created_at.desc()).all()


@router.get("/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/{course_id}/enroll", response_model=schemas.EnrollmentOut)
def enroll(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("student")),
):
    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    existing = db.query(models.Enrollment).filter_by(student_id=current_user.id, course_id=course_id).first()
    if existing:
        return existing
    enrollment = models.Enrollment(student_id=current_user.id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/mine/enrollments", response_model=List[schemas.EnrollmentOut])
def my_enrollments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Enrollment).filter_by(student_id=current_user.id).all()
