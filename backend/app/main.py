"""
Application entry point. Wires up CORS, DB init, and all routers.
Run with: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import (
    auth, courses, materials, search, assistant,
    studygen, knowledge_graph, analytics, assignments, admin,
)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}


app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(materials.router)
app.include_router(search.router)
app.include_router(assistant.router)
app.include_router(studygen.router)
app.include_router(knowledge_graph.router)
app.include_router(analytics.router)
app.include_router(assignments.router)
app.include_router(admin.router)
