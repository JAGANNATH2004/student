"""
SQLAlchemy ORM models.

The Knowledge Graph (Module 5) is intentionally modeled as relational tables
(Concept + ConceptEdge) instead of requiring a Neo4j server. Graph traversal
(prerequisite chains, related concepts) is done in Python in graph_service.py.
This keeps the whole project runnable with zero external DB services while
preserving the same functionality described in the project spec.
"""
import enum
import datetime as dt

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float,
    Enum as SAEnum, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


def now():
    return dt.datetime.utcnow()


class UserRole(str, enum.Enum):
    student = "student"
    faculty = "faculty"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(190), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.student, nullable=False)
    created_at = Column(DateTime, default=now)
    is_active = Column(Boolean, default=True)

    courses_taught = relationship("Course", back_populates="instructor")
    enrollments = relationship("Enrollment", back_populates="student")
    chat_messages = relationship("ChatMessage", back_populates="user")
    quiz_attempts = relationship("QuizAttempt", back_populates="student")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="student")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    description = Column(Text, default="")
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=now)

    instructor = relationship("User", back_populates="courses_taught")
    materials = relationship("Material", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    concepts = relationship("Concept", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_enrollment"),)

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=now)
    progress_percent = Column(Float, default=0.0)

    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class MaterialType(str, enum.Enum):
    pdf = "pdf"
    ppt = "ppt"
    video = "video"
    note = "note"


class Material(Base):
    """An uploaded learning resource (Module 2 & 3)."""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    material_type = Column(SAEnum(MaterialType), nullable=False)
    file_path = Column(String(500), nullable=True)   # local path for pdf/ppt
    video_url = Column(String(500), nullable=True)   # external link for videos
    raw_text = Column(Text, default="")               # extracted text
    is_indexed = Column(Boolean, default=False)        # embedded into vector store?
    uploaded_at = Column(DateTime, default=now)

    course = relationship("Course", back_populates="materials")
    chunks = relationship("MaterialChunk", back_populates="material", cascade="all, delete-orphan")


class MaterialChunk(Base):
    """
    A semantic chunk of a material's text. The chunk text is duplicated here
    (source of truth) and also pushed into ChromaDB (vector index) keyed by
    this row's id, so search results can be traced back to their source
    material — this is what powers source attribution in Module 8.
    """
    __tablename__ = "material_chunks"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    material = relationship("Material", back_populates="chunks")


class Concept(Base):
    """A node in the Knowledge Graph (Module 5)."""
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")

    course = relationship("Course", back_populates="concepts")


class ConceptEdgeType(str, enum.Enum):
    prerequisite = "prerequisite"     # source is a prerequisite of target
    related = "related"               # loosely related concept
    leads_to_outcome = "leads_to_outcome"  # concept -> learning outcome


class ConceptEdge(Base):
    """A directed edge between two concepts (models the graph relationships)."""
    __tablename__ = "concept_edges"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    edge_type = Column(SAEnum(ConceptEdgeType), default=ConceptEdgeType.related)

    source = relationship("Concept", foreign_keys=[source_id])
    target = relationship("Concept", foreign_keys=[target_id])


class ChatMessage(Base):
    """AI Learning Assistant conversation history (Module 6, RAG-backed)."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    role = Column(String(20), nullable=False)   # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=list)          # list of {material_id, title, snippet}
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=now)

    user = relationship("User", back_populates="chat_messages")


class Quiz(Base):
    """AI-generated or instructor quiz (Module 4 study material generator)."""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    source_material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)
    questions = Column(JSON, nullable=False)  # list of {question, options[], answer_index, explanation}
    created_at = Column(DateTime, default=now)

    course = relationship("Course", back_populates="quizzes")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answers = Column(JSON, default=list)     # list of selected option indices
    score_percent = Column(Float, default=0.0)
    submitted_at = Column(DateTime, default=now)

    student = relationship("User", back_populates="quiz_attempts")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    instructions = Column(Text, default="")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=now)

    course = relationship("Course", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentSubmission(Base):
    """Student submission with optional AI preliminary evaluation (Module 7)."""
    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    ai_relevance_score = Column(Float, nullable=True)
    ai_completeness_score = Column(Float, nullable=True)
    ai_writing_quality_score = Column(Float, nullable=True)
    ai_concept_coverage_score = Column(Float, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=now)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="assignment_submissions")


class LearningActivityLog(Base):
    """Raw activity events used as input to the analytics/prediction engine."""
    __tablename__ = "learning_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # "material_view","quiz_attempt","chat_query","assignment_submit"
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=now)


class LearningPath(Base):
    """Personalized learning path output (Module 4)."""
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    generated_at = Column(DateTime, default=now)
    steps = Column(JSON, nullable=False)  # ordered list of {concept, reason, type}
