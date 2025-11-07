# Demo Forums API

A simple FastAPI-based backend for the Demo Forums project, designed for learning and testing frontend technologies.

## Purpose

This API replaces MSW (Mock Service Worker) mocks with a real backend service. It stores all data in memory, making it perfect for development and experimentation without database setup.

**Note**: All data is volatile and resets when the server restarts.

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.14** - Latest Python version
- **uv** - Fast Python package manager
- In-memory data storage (no database required)

## Quick Start

### Prerequisites

- Python 3.14+
- uv package manager

### Installation & Running

```bash
# Install dependencies
uv sync

# Run the development server
uv run uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/logout` - Logout and invalidate session

### Profile
- `GET /api/profile` - Get current user profile
- `POST /api/profile/change-password` - Change password

### Forums
- `GET /api/forums` - Get all forums
- `POST /api/forums` - Create new forum (admin only)

### Posts
- `GET /api/forums/{slug}/posts` - Get posts with pagination
- `GET /api/forums/{slug}/posts/{postNumber}` - Get single post
- `POST /api/forums/{slug}/posts` - Create new post

### Comments
- `GET /api/forums/{slug}/posts/{postNumber}/comments` - Get all comments
- `POST /api/forums/{slug}/posts/{postNumber}/comments` - Create comment

### Users
- `GET /api/users` - Get all users

## Pre-loaded Data

The API comes with pre-populated data:

**Users**:
- `admin` / `admin` (admin role)
- `user1` / `user1` (user role)
- Plus additional test users (alice, bob)

**Forums**: 9 forums across 3 categories:
- Technology: web-development, artificial-intelligence, mobile-development
- Science: physics, biology, chemistry
- Art: digital-art, traditional-art, photography

**Posts & Comments**: Sample posts and comments are generated for testing.

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## CORS

The API is configured to work with the React Router frontend project at `http://localhost:5173`.
