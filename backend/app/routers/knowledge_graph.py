"""Module 5 — Knowledge Graph-Based Learning Navigation."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, require_roles
from app.services.graph_service import get_course_graph, get_prerequisite_chain, get_related_concepts

router = APIRouter(prefix="/api/graph", tags=["Knowledge Graph"])


@router.post("/concepts", response_model=schemas.ConceptOut)
def create_concept(
    payload: schemas.ConceptCreate, db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("faculty", "admin")),
):
    concept = models.Concept(course_id=payload.course_id, name=payload.name, description=payload.description)
    db.add(concept)
    db.commit()
    db.refresh(concept)
    return concept


@router.post("/edges")
def create_edge(
    payload: schemas.ConceptEdgeCreate, db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles("faculty", "admin")),
):
    if payload.edge_type not in [e.value for e in models.ConceptEdgeType]:
        raise HTTPException(status_code=400, detail="Invalid edge_type")
    edge = models.ConceptEdge(
        source_id=payload.source_id, target_id=payload.target_id,
        edge_type=models.ConceptEdgeType(payload.edge_type),
    )
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return {"id": edge.id, "source_id": edge.source_id, "target_id": edge.target_id, "edge_type": edge.edge_type.value}


@router.get("/course/{course_id}", response_model=schemas.GraphResponse)
def course_graph(course_id: int, db: Session = Depends(get_db)):
    return get_course_graph(db, course_id)


@router.get("/concepts/{concept_id}/prerequisites", response_model=List[schemas.ConceptOut])
def prerequisites(concept_id: int, db: Session = Depends(get_db)):
    return get_prerequisite_chain(db, concept_id)


@router.get("/concepts/{concept_id}/related", response_model=List[schemas.ConceptOut])
def related(concept_id: int, db: Session = Depends(get_db)):
    return get_related_concepts(db, concept_id)
