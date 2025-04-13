"""FastAPI Contact Management Application.

This is the main application module that sets up the FastAPI instance,
configures middleware, exception handlers, and includes all API routers.

The application provides:
- User authentication and management
- Contact management with CRUD operations
- Rate limiting
- CORS support
- Health checking utilities

Environment variables required:
- Database configuration (see config.py)
- JWT settings for authentication
- Cloudinary settings for avatar storage
"""

from src.api import auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.api import utils, contacts, users


app = FastAPI(
    title="Contact Management API",
    description="REST API for managing contacts with user authentication",
    version="1.0.0",
)

# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded exceptions.

    This handler returns a 429 Too Many Requests response when a client
    exceeds the rate limit for any endpoint.

    Args:
        request (Request): The incoming request that exceeded the rate limit.
        exc (RateLimitExceeded): The rate limit exception.

    Returns:
        JSONResponse: Error response with 429 status code.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Rate limit exceeded. Please try again later."},
    )


# Include routers with /api prefix
app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    # Run the application with hot reload enabled
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
