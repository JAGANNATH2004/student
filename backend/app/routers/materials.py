"""
Module 3 — AI Learning Repository: upload PDFs/PPTs/videos, extract text,
chunk it, and index it into the vector store for semantic search + RAG.
"""
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.deps import get_db, require_roles, get_current_user
from app.services.document_processor import process_file, chunk_text
from app.services.vector_store import index_chunks

router = APIRouter(prefix="/api/materials", tags=["Materials"])

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


def _index_material_background(material_id: int):
    """Runs after upload: extract -> chunk -> embed -> store. Kept sync-friendly
    for simplicity; swap for a task queue (Celery/RQ) in a production deploy."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        material = db.query(models.Material).get(material_id)
        if not material or not material.file_path:
            return
        text = process_file(material.file_path, material.material_type.value)
        material.raw_text = text
        chunks = chunk_text(text)

        db.query(models.MaterialChunk).filter_by(material_id=material.id).delete()
        chunk_rows = []
        for i, c in enumerate(chunks):
            row = models.MaterialChunk(material_id=material.id, chunk_index=i, text=c)
            db.add(row)
            chunk_rows.append(row)
        db.flush()

        if chunk_rows:
            index_chunks(
                course_id=material.course_id,
                material_id=material.id,
                chunk_ids=[r.id for r in chunk_rows],
                chunks=[r.text for r in chunk_rows],
                titles=[material.title] * len(chunk_rows),
            )
        material.is_indexed = True
        db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=schemas.MaterialOut)
def upload_material(
    background_tasks: BackgroundTasks,
    course_id: int = Form(...),
    title: str = Form(...),
    material_type: str = Form(...),  # "pdf" | "ppt"
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("faculty", "admin")),
):
    if material_type not in ("pdf", "ppt"):
        raise HTTPException(status_code=400, detail="material_type must be 'pdf' or 'ppt'")

    course = db.query(models.Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    ext = "pdf" if material_type == "pdf" else "pptx"
    filename = f"{uuid.uuid4().hex}.{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(dest_path, "wb") as f:
        f.write(file.file.read())

    material = models.Material(
        course_id=course_id, title=title,
        material_type=models.MaterialType(material_type),
        file_path=dest_path,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    background_tasks.add_task(_index_material_background, material.id)
    return material


@router.post("/video", response_model=schemas.MaterialOut)
def add_video_material(
    payload: schemas.VideoMaterialCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("faculty", "admin")),
):
    """Video metadata indexing (spec: video URL + title, searchable by title/description)."""
    course = db.query(models.Course).get(payload.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    material = models.Material(
        course_id=payload.course_id, title=payload.title,
        material_type=models.MaterialType.video, video_url=payload.video_url,
        is_indexed=True,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.get("/course/{course_id}", response_model=List[schemas.MaterialOut])
def list_materials(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Material).filter(models.Material.course_id == course_id).all()


@router.get("/{material_id}")
def get_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(models.Material).get(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return {
        "id": material.id, "title": material.title,
        "material_type": material.material_type.value,
        "is_indexed": material.is_indexed,
        "raw_text_preview": (material.raw_text or "")[:1000],
        "video_url": material.video_url,
    }


@router.post("/{material_id}/log-view")
def log_material_view(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("student")),
):
    """Records a view event, feeding the analytics/prediction engine."""
    material = db.query(models.Material).get(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    log = models.LearningActivityLog(
        student_id=current_user.id, course_id=material.course_id,
        activity_type="material_view", metadata_json={"material_id": material_id},
    )
    db.add(log)
    db.commit()
    return {"status": "logged"}
