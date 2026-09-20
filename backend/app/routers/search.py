"""Module 6 (search half) — Intelligent Academic Search: semantic, not keyword."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.deps import get_db
from app.services.vector_store import semantic_search

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("/{course_id}", response_model=List[schemas.SearchResult])
def search_course(course_id: int, q: str, top_k: int = 5, db: Session = Depends(get_db)):
    results = semantic_search(course_id, q, top_k=top_k)
    return [
        schemas.SearchResult(
            material_id=r["material_id"], material_title=r["material_title"],
            chunk_text=r["chunk_text"], score=r["score"],
        )
        for r in results
    ]
