from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import projects, entries, templates

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AutoDoc API",
    description="Backend for AutoDoc – persistent projects, entries, and templates",
    version="1.0.0",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Allow the React dev server (localhost:3000) and any same-origin requests.
# In production narrow this down to your actual domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(projects.router)
app.include_router(entries.router)
app.include_router(templates.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
