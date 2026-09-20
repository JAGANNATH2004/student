# Athenaeum — AI-Powered Intelligent E-Learning & Personalized Learning Analytics Platform

A complete, runnable implementation of the project brief: an e-learning platform that goes
beyond a traditional LMS by integrating **Large Language Models**, **Retrieval-Augmented
Generation (RAG)**, a **Knowledge Graph**, **Explainable Learning Analytics**, and an
**AI Study Material Generator**.

---

## 1. Project overview

Instructors upload course material (PDF/PPT/video links). The platform extracts and
semantically indexes that material, then:

- Answers student questions **grounded in the actual course content** (RAG), with sources
  cited and a visible confidence score.
- Generates **summaries, flashcards, quizzes, and revision notes** from any uploaded file.
- Models course concepts and their **prerequisite relationships** as a knowledge graph,
  and uses it to generate **personalized learning paths**.
- Predicts student performance and **explains the prediction** in plain language instead of
  just showing a number (Explainable AI).
- Gives students **preliminary AI feedback** on written assignment answers.
- Gives faculty/admins a **dashboard** of course engagement and quiz performance.

## 2. Technology stack & why

| Layer | Choice | Why |
|---|---|---|
| Frontend | React 18 + Vite + Tailwind CSS | Matches the spec's frontend stack; Vite gives instant dev reload |
| Backend | Python + FastAPI | Matches the spec; async-friendly, auto-generates OpenAPI docs at `/docs` |
| Database | SQLite via SQLAlchemy (swap to PostgreSQL by changing one env var) | Zero-setup by default — runs with no external DB server. `DATABASE_URL` change is all that's needed to point at real PostgreSQL in production |
| Knowledge Graph | Modeled as relational tables (`Concept`, `ConceptEdge`) with graph traversal in Python | Delivers the exact same functionality as the spec's Neo4j suggestion, without requiring you to install and run a separate graph database server |
| Vector store | ChromaDB (embedded/local, no server process) | Matches the spec's suggestion (FAISS/ChromaDB); needs no separate service |
| Embeddings | `sentence-transformers` (local, free) or OpenAI embeddings — switch via `.env` | Works fully offline by default |
| LLM | OpenAI API or local Ollama (Llama 3 / Mistral) — switch via `.env` | Pluggable so you aren't locked into a paid API |
| Auth | JWT (python-jose) + bcrypt password hashing | Simple, standard, stateless |

This is a genuinely simplified-but-complete version of the "Full stack: PostgreSQL + Neo4j"
architecture described in the source proposal — every module and feature from the spec is
implemented, just without requiring you to install and run three separate database servers
before you can see it work.

## 3. Folder structure

```
ai-elearning-platform/
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── config.py                # env-based settings
│   │   ├── database.py              # SQLAlchemy engine/session
│   │   ├── models.py                # ORM models (users, courses, graph, quizzes, ...)
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── auth.py                  # password hashing + JWT
│   │   ├── deps.py                  # FastAPI dependencies (auth, roles)
│   │   ├── routers/
│   │   │   ├── auth.py              # register/login
│   │   │   ├── courses.py           # course CRUD + enrollment
│   │   │   ├── materials.py         # upload PDFs/PPTs/videos, indexing
│   │   │   ├── search.py            # semantic search endpoint
│   │   │   ├── assistant.py         # RAG chat endpoint
│   │   │   ├── studygen.py          # summary/flashcards/quiz generation
│   │   │   ├── knowledge_graph.py   # concept graph CRUD + navigation
│   │   │   ├── analytics.py         # explainable analytics + learning paths
│   │   │   ├── assignments.py       # assignments + AI evaluation
│   │   │   └── admin.py             # admin/faculty dashboard stats
│   │   └── services/
│   │       ├── document_processor.py  # PDF/PPT text extraction + chunking
│   │       ├── embeddings.py          # local or OpenAI embedding provider
│   │       ├── vector_store.py        # ChromaDB wrapper
│   │       ├── llm_client.py          # pluggable OpenAI/Ollama chat client
│   │       ├── rag_engine.py          # retrieval + grounded generation
│   │       ├── graph_service.py       # graph traversal (prerequisites, related)
│   │       ├── study_generator.py     # AI summaries/flashcards/quizzes
│   │       ├── assignment_evaluator.py# AI preliminary grading
│   │       └── analytics_engine.py    # performance prediction + explanations
│   ├── seed.py                      # demo data (users, course, concepts)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx / App.jsx
│   │   ├── api/client.js            # axios instance + auth interceptor
│   │   ├── context/AuthContext.jsx  # login/register/logout state
│   │   ├── components/              # Navbar, ProtectedRoute, Loading, etc.
│   │   └── pages/                   # Login, Register, Courses, AI Assistant,
│   │                                 # Knowledge Graph, Study Materials, Analytics,
│   │                                 # Assignments, Admin Dashboard
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
│
├── docker-compose.yml                # optional containerized dev setup
├── .gitignore
└── README.md
```

## 4. Database schema (key tables)

- **users** — id, full_name, email, hashed_password, role (student/faculty/admin)
- **courses** — id, title, code, description, instructor_id
- **enrollments** — student_id, course_id, progress_percent
- **materials** — course_id, title, material_type (pdf/ppt/video), file_path, raw_text, is_indexed
- **material_chunks** — material_id, chunk_index, text (source of truth backing the vector store)
- **concepts** — course_id, name, description (Knowledge Graph nodes)
- **concept_edges** — source_id, target_id, edge_type (prerequisite/related/leads_to_outcome)
- **chat_messages** — user_id, course_id, role, content, sources (JSON), confidence
- **quizzes** / **quiz_attempts** — AI-generated questions + student attempts/scores
- **assignments** / **assignment_submissions** — instructions + student answers + AI scores
- **learning_activity_logs** — raw events feeding the analytics engine
- **learning_paths** — generated personalized study sequences

## 5. API endpoint list

All endpoints are prefixed `/api`. Full interactive docs at **`http://localhost:8000/docs`**
once the backend is running.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create account, returns JWT |
| POST | `/api/auth/login` | Login, returns JWT |
| POST | `/api/courses` | Create course (faculty/admin) |
| GET | `/api/courses` | List all courses |
| GET | `/api/courses/{id}` | Get one course |
| POST | `/api/courses/{id}/enroll` | Enroll (student) |
| GET | `/api/courses/mine/enrollments` | My enrollments |
| POST | `/api/materials/upload` | Upload PDF/PPT (background text extraction + indexing) |
| POST | `/api/materials/video` | Add a video resource |
| GET | `/api/materials/course/{course_id}` | List materials for a course |
| GET | `/api/materials/{id}` | Get one material (with text preview) |
| POST | `/api/materials/{id}/log-view` | Log a view (feeds analytics) |
| GET | `/api/search/{course_id}?q=...` | Semantic search within a course |
| POST | `/api/assistant/ask` | Ask the RAG-powered AI Learning Assistant |
| GET | `/api/assistant/history` | Chat history |
| POST | `/api/study/generate` | Generate summary/flashcards/quiz/notes from a material |
| GET | `/api/study/quizzes/course/{course_id}` | List quizzes |
| GET | `/api/study/quizzes/{id}` | Get quiz questions |
| POST | `/api/study/quizzes/submit` | Submit quiz answers, get scored review |
| POST | `/api/graph/concepts` | Add a knowledge-graph concept |
| POST | `/api/graph/edges` | Link two concepts |
| GET | `/api/graph/course/{course_id}` | Full graph for a course |
| GET | `/api/graph/concepts/{id}/prerequisites` | Prerequisite chain |
| GET | `/api/graph/concepts/{id}/related` | Related concepts |
| GET | `/api/analytics/course/{course_id}` | My explainable analytics |
| GET | `/api/analytics/course/{course_id}/student/{student_id}` | (faculty) a student's analytics |
| GET | `/api/analytics/course/{course_id}/learning-path` | Personalized learning path |
| POST | `/api/assignments` | Create assignment (faculty) |
| GET | `/api/assignments/course/{course_id}` | List assignments |
| POST | `/api/assignments/submit` | Submit answer, get AI preliminary feedback |
| GET | `/api/assignments/{id}/submissions` | (faculty) view submissions |
| GET | `/api/admin/overview` | Platform-wide dashboard stats |

## 6. Application workflow

1. **Register** as faculty → create a course → **upload** a PDF/PPT.
2. The backend extracts text, chunks it, embeds it, and stores it in ChromaDB
   (visible as `is_indexed: true` once done — usually a few seconds).
3. Faculty adds **concepts** and links them (prerequisite/related) to build the
   course's knowledge graph.
4. A **student** registers, enrolls in the course, and can:
   - Ask the **AI Assistant** questions — answers are grounded in the uploaded material.
   - Open **Study tools** on any material to generate a summary, flashcards, or a quiz.
   - Take quizzes; scores feed the analytics engine.
   - View their **Knowledge Graph**, **Progress/Analytics**, and **personalized learning path**.
   - Submit assignment answers and get preliminary AI feedback.
5. Faculty/admin can view the **Dashboard** for engagement and quiz-performance stats.

---

## 7. Installation & running it locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- An OpenAI API key **or** a locally running [Ollama](https://ollama.com) instance

### 7.1 Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env:
#   - Set OPENAI_API_KEY=sk-...          (if LLM_PROVIDER=openai, the default)
#   - OR set LLM_PROVIDER=ollama and make sure `ollama serve` is running with
#     `ollama pull llama3` done beforehand.
#   - EMBEDDING_PROVIDER=local works out of the box, no key needed.

python seed.py                  # creates demo faculty/admin/student + a sample course
uvicorn app.main:app --reload   # starts on http://localhost:8000
```

Interactive API docs: **http://localhost:8000/docs**

### 7.2 Frontend setup

```bash
cd frontend
npm install
cp .env.example .env            # defaults to http://localhost:8000, fine for local dev
npm run dev                     # starts on http://localhost:5173
```

Open **http://localhost:5173** in your browser.

### 7.3 Try it out

Demo accounts (created by `seed.py`), all with password `password123`:

- `faculty@example.com` — upload materials, build the knowledge graph, create assignments
- `admin@example.com` — view the platform dashboard
- `student@example.com` — already enrolled in the demo "CS401 — Computer Networks" course

### 7.4 Switching to PostgreSQL (optional)

```bash
pip install psycopg2-binary
```
Then in `backend/.env`:
```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/elearning
```
No other code changes needed — SQLAlchemy handles the rest.

### 7.5 Docker (optional)

```bash
docker compose up --build
```

---

## 8. Testing the application

1. Register a faculty account → create a course → upload a PDF. Wait ~5–15 seconds
   (depends on file size / embedding model download on first run), then refresh the
   course page — the material should show **"Indexed"**.
2. Register a student account → enroll in the course.
3. Go to **AI Assistant**, select the course, and ask a question about the uploaded content —
   confirm the answer cites the material as a source.
4. Open **Study tools** on the material and generate a quiz; take it and confirm scoring works.
5. As faculty, add 2–3 concepts and link them with `prerequisite` edges; as a student, view
   **Knowledge graph** to confirm the diagram renders.
6. As a student, view **My Progress** — confirm the analytics and learning path populate
   (scores improve as you take more quizzes).
7. Check **`/api/admin/overview`** via the Dashboard as faculty/admin.

## 9. Common errors & solutions

| Symptom | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` on every request | Missing/expired JWT | Log in again; check `localStorage` has a `token` |
| AI Assistant / study generation returns an error | No `OPENAI_API_KEY` set, or Ollama not running | Set a valid key in `.env`, or start `ollama serve` and set `LLM_PROVIDER=ollama` |
| Material stays "Processing…" forever | Extraction failed (corrupted file) or embedding model still downloading on first run | Check backend logs; the first `sentence-transformers` call downloads the model (~90MB) and needs internet access once |
| `CORS` errors in the browser console | Frontend origin doesn't match `FRONTEND_ORIGIN` in backend `.env` | Set `FRONTEND_ORIGIN=http://localhost:5173` (default) or update to match your dev URL |
| `sqlite3.OperationalError: database is locked` | Rare under heavy concurrent writes on SQLite | Switch to PostgreSQL for multi-user production use (see 7.4) |
| `ModuleNotFoundError` on backend start | Virtualenv not activated or deps not installed | Re-run `pip install -r requirements.txt` inside the activated venv |
| Flashcards/quiz JSON parsing errors | LLM occasionally wraps JSON in prose despite instructions | Retry generation; `study_generator.py`'s `_extract_json` already strips common wrapping, but very small/free local models are less reliable at strict JSON than GPT-4-class models |

## 10. Security notes

- No secrets are hard-coded anywhere — everything sensitive is read from `.env` (see
  `backend/.env.example`), which is git-ignored.
- Passwords are hashed with bcrypt; never stored in plain text.
- JWTs expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 24h).
- Role-based guards (`require_roles`) protect faculty/admin-only endpoints.
- Before deploying publicly: put this behind HTTPS, rotate `SECRET_KEY`, add rate limiting,
  and validate/limit file upload size and types more strictly.
