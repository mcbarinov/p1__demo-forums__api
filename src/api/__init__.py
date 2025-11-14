from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Convert Pydantic validation errors (422) to 400 with clear error messages"""
    errors = exc.errors()

    # Build a user-friendly error message
    if errors:
        first_error = errors[0]
        field_path = " -> ".join(str(loc) for loc in first_error["loc"] if loc != "body")
        error_type = first_error["type"]

        # Create human-readable messages based on error type
        if error_type == "string_too_short":
            min_length = first_error.get("ctx", {}).get("min_length", "required")
            message = f"Field '{field_path}' must be at least {min_length} characters long"
        elif error_type == "missing":
            message = f"Field '{field_path}' is required"
        elif error_type in ("string_type", "int_parsing", "float_parsing"):
            message = f"Invalid value for field '{field_path}'"
        else:
            # Fallback to original message
            message = first_error.get("msg", "Validation error")
    else:
        message = "Validation error"

    return JSONResponse(status_code=400, content={"message": message, "type": "validation_error"})


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """Convert HTTPException to ErrorResponse format"""
    # Map status codes to error types
    error_type_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        422: "validation_error",
        500: "internal_error",
    }

    error_type = error_type_map.get(exc.status_code, "error")

    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail, "type": error_type})


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
