"""
Seeds the database with demo users, a course, and a knowledge graph so you
can explore the whole platform immediately after setup.

Run with:  python seed.py
"""
from app.database import SessionLocal, init_db
from app import models
from app.auth import hash_password

init_db()
db = SessionLocal()

def get_or_create_user(full_name, email, password, role):
    user = db.query(models.User).filter_by(email=email).first()
    if user:
        return user
    user = models.User(
        full_name=full_name, email=email,
        hashed_password=hash_password(password), role=models.UserRole(role),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

faculty = get_or_create_user("Dr. Asha Rao", "faculty@example.com", "password123", "faculty")
admin = get_or_create_user("Platform Admin", "admin@example.com", "password123", "admin")
student = get_or_create_user("Ravi Kumar", "student@example.com", "password123", "student")

course = db.query(models.Course).filter_by(code="CS401").first()
if not course:
    course = models.Course(
        title="Computer Networks", code="CS401",
        description="Fundamentals of computer networking, routing, and protocols.",
        instructor_id=faculty.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

if not db.query(models.Enrollment).filter_by(student_id=student.id, course_id=course.id).first():
    db.add(models.Enrollment(student_id=student.id, course_id=course.id))

concept_names = ["Networking Basics", "OSI Model", "Routing Algorithms", "TCP/IP", "Network Security"]
concepts = {}
for name in concept_names:
    c = db.query(models.Concept).filter_by(course_id=course.id, name=name).first()
    if not c:
        c = models.Concept(course_id=course.id, name=name, description=f"Overview of {name}.")
        db.add(c)
        db.commit()
        db.refresh(c)
    concepts[name] = c

def link(src, tgt, edge_type):
    exists = db.query(models.ConceptEdge).filter_by(
        source_id=concepts[src].id, target_id=concepts[tgt].id,
    ).first()
    if not exists:
        db.add(models.ConceptEdge(
            source_id=concepts[src].id, target_id=concepts[tgt].id,
            edge_type=models.ConceptEdgeType(edge_type),
        ))

link("Networking Basics", "OSI Model", "prerequisite")
link("OSI Model", "Routing Algorithms", "prerequisite")
link("OSI Model", "TCP/IP", "prerequisite")
link("TCP/IP", "Network Security", "prerequisite")
link("Routing Algorithms", "TCP/IP", "related")
course_id = course.id
db.commit()
db.close()

print("Seed complete.")
print("Login as faculty:  faculty@example.com / password123")
print("Login as admin:    admin@example.com / password123")
print("Login as student:  student@example.com / password123")
print(f"Demo course code: CS401 (id={course_id})")
