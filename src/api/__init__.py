from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .openapi import set_custom_openapi
from .routes import (
    auth_router,
    comments_router,
    forums_router,
    posts_router,
    profile_router,
    users_router,
)

app = FastAPI(
    title="Demo Forums API",
    description="Backend API for Demo Forums - A learning project for frontend technologies",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(forums_router, prefix="/api")
app.include_router(posts_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(users_router, prefix="/api")

# Set custom OpenAPI schema
set_custom_openapi(app)


@app.get("/")
def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok", "message": "Demo Forums API is running"}
