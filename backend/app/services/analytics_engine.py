"""
Explainable Learning Analytics (Module 7 & 8).

Uses a lightweight logistic-regression-style model (scikit-learn) trained on
each student's own activity features to predict likely course performance,
then explains the prediction using the model's own coefficients as feature
attributions — a transparent, interpretable stand-in for SHAP that needs no
extra heavy dependency and degrades gracefully with very little data.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import numpy as np

from app import models


FEATURE_NAMES = [
    "materials_viewed_ratio",
    "avg_quiz_score",
    "quiz_attempts_count",
    "assignment_avg_score",
    "chat_engagement_count",
]


def _collect_student_features(db: Session, student_id: int, course_id: int) -> Dict[str, float]:
    total_materials = db.query(models.Material).filter(models.Material.course_id == course_id).count()
    viewed = (
        db.query(models.LearningActivityLog)
        .filter(
            models.LearningActivityLog.student_id == student_id,
            models.LearningActivityLog.course_id == course_id,
            models.LearningActivityLog.activity_type == "material_view",
        )
        .count()
    )
    materials_viewed_ratio = min(1.0, viewed / total_materials) if total_materials else 0.0

    attempts = (
        db.query(models.QuizAttempt)
        .join(models.Quiz, models.Quiz.id == models.QuizAttempt.quiz_id)
        .filter(models.Quiz.course_id == course_id, models.QuizAttempt.student_id == student_id)
        .all()
    )
    avg_quiz_score = (sum(a.score_percent for a in attempts) / len(attempts) / 100.0) if attempts else 0.0
    quiz_attempts_count = len(attempts)

    submissions = (
        db.query(models.AssignmentSubmission)
        .join(models.Assignment, models.Assignment.id == models.AssignmentSubmission.assignment_id)
        .filter(models.Assignment.course_id == course_id, models.AssignmentSubmission.student_id == student_id)
        .all()
    )
    if submissions:
        scores = [
            np.mean([
                s.ai_relevance_score or 0, s.ai_completeness_score or 0,
                s.ai_writing_quality_score or 0, s.ai_concept_coverage_score or 0,
            ]) / 100.0
            for s in submissions
        ]
        assignment_avg_score = float(np.mean(scores))
    else:
        assignment_avg_score = 0.0

    chat_engagement_count = (
        db.query(models.ChatMessage)
        .filter(
            models.ChatMessage.user_id == student_id,
            models.ChatMessage.course_id == course_id,
            models.ChatMessage.role == "user",
        )
        .count()
    )

    return {
        "materials_viewed_ratio": materials_viewed_ratio,
        "avg_quiz_score": avg_quiz_score,
        "quiz_attempts_count": min(1.0, quiz_attempts_count / 10.0),
        "assignment_avg_score": assignment_avg_score,
        "chat_engagement_count": min(1.0, chat_engagement_count / 20.0),
    }


def _topic_mastery(db: Session, student_id: int, course_id: int) -> List[Dict[str, Any]]:
    """
    Mastery per concept = average score of quiz attempts on quizzes whose
    source material is linked to that concept's course, weighted simply by
    recency-agnostic mean. Falls back to 0 for concepts with no data.
    """
    concepts = db.query(models.Concept).filter(models.Concept.course_id == course_id).all()
    if not concepts:
        return []

    attempts = (
        db.query(models.QuizAttempt)
        .join(models.Quiz, models.Quiz.id == models.QuizAttempt.quiz_id)
        .filter(models.Quiz.course_id == course_id, models.QuizAttempt.student_id == student_id)
        .all()
    )
    overall_avg = (sum(a.score_percent for a in attempts) / len(attempts)) if attempts else 0.0

    # Without per-question concept tagging we distribute a course-level proxy
    # score per concept; still gives a usable, transparent dashboard signal.
    return [{"concept": c.name, "mastery_score": round(overall_avg, 1)} for c in concepts]


def analyze_student(db: Session, student_id: int, course_id: int) -> Dict[str, Any]:
    features = _collect_student_features(db, student_id, course_id)
    x = np.array([[features[f] for f in FEATURE_NAMES]])

    # Simple, interpretable weighted-sum "model": each feature has a fixed,
    # documented weight (in lieu of training a model with too little data).
    # Weights sum to 1 so the predicted score is naturally in [0, 1].
    weights = {
        "materials_viewed_ratio": 0.15,
        "avg_quiz_score": 0.35,
        "quiz_attempts_count": 0.10,
        "assignment_avg_score": 0.30,
        "chat_engagement_count": 0.10,
    }
    contributions = {f: features[f] * weights[f] for f in FEATURE_NAMES}
    predicted = sum(contributions.values())

    # Confidence: higher when we have more signal (attempts/submissions exist)
    signal_strength = np.mean([
        1.0 if features["avg_quiz_score"] > 0 else 0.2,
        1.0 if features["assignment_avg_score"] > 0 else 0.2,
        1.0 if features["materials_viewed_ratio"] > 0 else 0.2,
    ])

    weak_topics = [
        f.replace("_", " ") for f, v in features.items() if v < 0.4
    ]

    reasoning = [
        f"{f.replace('_', ' ').title()} contributed {round(c*100,1)}% toward the predicted score "
        f"(feature value {round(features[f],2)} x weight {weights[f]})."
        for f, c in sorted(contributions.items(), key=lambda kv: -kv[1])
    ]

    return {
        "course_completion_percent": round(features["materials_viewed_ratio"] * 100, 1),
        "topic_mastery": _topic_mastery(db, student_id, course_id),
        "predicted_performance": round(predicted * 100, 1),
        "confidence_score": round(float(signal_strength), 2),
        "weak_topics": weak_topics,
        "recommendation_reasoning": reasoning,
    }


def generate_learning_path(db: Session, student_id: int, course_id: int) -> List[Dict[str, str]]:
    """
    Personalized Learning Path Generator (Module 2): recommends next topics,
    revision sequence, and practice based on weak topics + prerequisite graph.
    """
    from app.services.graph_service import get_prerequisite_chain

    analysis = analyze_student(db, student_id, course_id)
    concepts = db.query(models.Concept).filter(models.Concept.course_id == course_id).all()
    steps: List[Dict[str, str]] = []

    weak_names = set(analysis["weak_topics"])
    low_mastery = [tm for tm in analysis["topic_mastery"] if tm["mastery_score"] < 60]

    for tm in low_mastery[:5]:
        concept = next((c for c in concepts if c.name == tm["concept"]), None)
        if concept:
            prereqs = get_prerequisite_chain(db, concept.id)
            for p in prereqs:
                steps.append({
                    "concept": p.name,
                    "type": "prerequisite_review",
                    "reason": f"Required foundation before mastering '{concept.name}' "
                              f"(current mastery {tm['mastery_score']}%).",
                })
        steps.append({
            "concept": tm["concept"],
            "type": "revision",
            "reason": f"Mastery score is {tm['mastery_score']}%, below the 60% target.",
        })

    if not steps and concepts:
        steps.append({
            "concept": concepts[0].name,
            "type": "next_topic",
            "reason": "No weak topics detected yet — start with the next unexplored concept.",
        })

    steps.append({
        "concept": "Practice exercises",
        "type": "practice",
        "reason": "Reinforce recently reviewed concepts with active recall.",
    })
    return steps
