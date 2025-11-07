from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(
    title="Demo Forums API",
    description="Backend API for Demo Forums - A learning project for frontend technologies",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok", "message": "Demo Forums API is running"}
