"""Module 2 (assignments) + Module 7 (AI evaluation)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, require_roles, get_current_user
from app.services.assignment_evaluator import evaluate_submission

router = APIRouter(prefix="/api/assignments", tags=["Assignments"])


@router.post("", response_model=schemas.AssignmentOut)
def create_assignment(
    payload: schemas.AssignmentCreate, db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("faculty", "admin")),
):
    assignment = models.Assignment(**payload.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/course/{course_id}", response_model=List[schemas.AssignmentOut])
def list_assignments(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Assignment).filter(models.Assignment.course_id == course_id).all()


@router.post("/submit", response_model=schemas.SubmissionOut)
def submit_assignment(
    payload: schemas.SubmissionCreate, db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("student")),
):
    assignment = db.query(models.Assignment).get(payload.assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    ai_eval = evaluate_submission(assignment.instructions, payload.answer_text)

    submission = models.AssignmentSubmission(
        assignment_id=payload.assignment_id, student_id=current_user.id,
        answer_text=payload.answer_text,
        ai_relevance_score=ai_eval.get("relevance"),
        ai_completeness_score=ai_eval.get("completeness"),
        ai_writing_quality_score=ai_eval.get("writing_quality"),
        ai_concept_coverage_score=ai_eval.get("concept_coverage"),
        ai_feedback=ai_eval.get("feedback"),
    )
    db.add(submission)
    db.add(models.LearningActivityLog(
        student_id=current_user.id, course_id=assignment.course_id, activity_type="assignment_submit",
    ))
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/{assignment_id}/submissions", response_model=List[schemas.SubmissionOut])
def list_submissions(
    assignment_id: int, db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("faculty", "admin")),
):
    return db.query(models.AssignmentSubmission).filter_by(assignment_id=assignment_id).all()
