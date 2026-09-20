"""
Knowledge Graph service (Module 5) implemented over relational tables
(Concept + ConceptEdge) instead of Neo4j, so the graph works with zero
external services. Provides the same capabilities the spec asks for:
building concept relationships, prerequisite chains, and graph-based
navigation/exploration.
"""
from collections import deque
from typing import List, Dict, Set
from sqlalchemy.orm import Session

from app import models


def get_course_graph(db: Session, course_id: int) -> Dict:
    concepts = db.query(models.Concept).filter(models.Concept.course_id == course_id).all()
    concept_ids = {c.id for c in concepts}
    edges = (
        db.query(models.ConceptEdge)
        .filter(models.ConceptEdge.source_id.in_(concept_ids))
        .all()
    )
    return {
        "nodes": [{"id": c.id, "name": c.name, "description": c.description} for c in concepts],
        "edges": [{"source": e.source_id, "target": e.target_id, "type": e.edge_type.value} for e in edges],
    }


def get_prerequisite_chain(db: Session, concept_id: int) -> List[models.Concept]:
    """
    BFS backwards through 'prerequisite' edges to find everything the student
    should learn before this concept, in dependency order.
    """
    visited: Set[int] = set()
    order: List[int] = []
    queue = deque([concept_id])

    while queue:
        current = queue.popleft()
        prereq_edges = (
            db.query(models.ConceptEdge)
            .filter(
                models.ConceptEdge.target_id == current,
                models.ConceptEdge.edge_type == models.ConceptEdgeType.prerequisite,
            )
            .all()
        )
        for edge in prereq_edges:
            if edge.source_id not in visited:
                visited.add(edge.source_id)
                order.append(edge.source_id)
                queue.append(edge.source_id)

    order.reverse()  # earliest prerequisites first
    if not order:
        return []
    concepts = db.query(models.Concept).filter(models.Concept.id.in_(order)).all()
    by_id = {c.id: c for c in concepts}
    return [by_id[i] for i in order if i in by_id]


def get_related_concepts(db: Session, concept_id: int) -> List[models.Concept]:
    edges = (
        db.query(models.ConceptEdge)
        .filter(
            (models.ConceptEdge.source_id == concept_id) | (models.ConceptEdge.target_id == concept_id),
            models.ConceptEdge.edge_type == models.ConceptEdgeType.related,
        )
        .all()
    )
    related_ids = set()
    for e in edges:
        related_ids.add(e.target_id if e.source_id == concept_id else e.source_id)
    if not related_ids:
        return []
    return db.query(models.Concept).filter(models.Concept.id.in_(related_ids)).all()
