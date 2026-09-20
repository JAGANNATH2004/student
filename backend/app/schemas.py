"""Pydantic request/response schemas."""
from __future__ import annotations
import datetime as dt
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth / Users ----------
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "student"  # "student" | "faculty" | "admin"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    created_at: dt.datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Courses ----------
class CourseCreate(BaseModel):
    title: str
    code: str
    description: str = ""


class CourseOut(BaseModel):
    id: int
    title: str
    code: str
    description: str
    instructor_id: int
    created_at: dt.datetime

    class Config:
        from_attributes = True


class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    progress_percent: float

    class Config:
        from_attributes = True


# ---------- Materials ----------
class MaterialOut(BaseModel):
    id: int
    course_id: int
    title: str
    material_type: str
    is_indexed: bool
    uploaded_at: dt.datetime

    class Config:
        from_attributes = True


class VideoMaterialCreate(BaseModel):
    course_id: int
    title: str
    video_url: str


# ---------- Search / RAG ----------
class SearchResult(BaseModel):
    material_id: int
    material_title: str
    chunk_text: str
    score: float


class AssistantQuery(BaseModel):
    course_id: Optional[int] = None
    question: str


class AssistantAnswer(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float


# ---------- Knowledge graph ----------
class ConceptCreate(BaseModel):
    course_id: int
    name: str
    description: str = ""


class ConceptOut(BaseModel):
    id: int
    course_id: int
    name: str
    description: str

    class Config:
        from_attributes = True


class ConceptEdgeCreate(BaseModel):
    source_id: int
    target_id: int
    edge_type: str = "related"  # prerequisite | related | leads_to_outcome


class GraphNode(BaseModel):
    id: int
    name: str
    description: str = ""


class GraphEdge(BaseModel):
    source: int
    target: int
    type: str


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# ---------- Study material generation ----------
class GenerateRequest(BaseModel):
    material_id: int
    kind: str  # "summary" | "flashcards" | "quiz" | "revision_notes"
    num_items: int = 5


class Flashcard(BaseModel):
    question: str
    answer: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer_index: int
    explanation: str


class QuizOut(BaseModel):
    id: int
    title: str
    questions: List[QuizQuestion]

    class Config:
        from_attributes = True


class QuizSubmit(BaseModel):
    quiz_id: int
    answers: List[int]


class QuizResult(BaseModel):
    score_percent: float
    correct_count: int
    total: int
    review: List[Dict[str, Any]]


# ---------- Assignments ----------
class AssignmentCreate(BaseModel):
    course_id: int
    title: str
    instructions: str = ""
    due_date: Optional[dt.datetime] = None


class AssignmentOut(BaseModel):
    id: int
    course_id: int
    title: str
    instructions: str
    due_date: Optional[dt.datetime]

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    assignment_id: int
    answer_text: str


class SubmissionOut(BaseModel):
    id: int
    assignment_id: int
    answer_text: str
    ai_relevance_score: Optional[float]
    ai_completeness_score: Optional[float]
    ai_writing_quality_score: Optional[float]
    ai_concept_coverage_score: Optional[float]
    ai_feedback: Optional[str]
    submitted_at: dt.datetime

    class Config:
        from_attributes = True


# ---------- Analytics ----------
class TopicMastery(BaseModel):
    concept: str
    mastery_score: float


class AnalyticsOut(BaseModel):
    course_completion_percent: float
    topic_mastery: List[TopicMastery]
    predicted_performance: float
    confidence_score: float
    weak_topics: List[str]
    recommendation_reasoning: List[str]


class LearningPathStep(BaseModel):
    concept: str
    type: str
    reason: str


class LearningPathOut(BaseModel):
    steps: List[LearningPathStep]
