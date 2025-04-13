from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """Check the health of the application and database connection.

    This endpoint performs a simple database query to verify that:
    1. The application is running and responding to requests
    2. The database connection is properly configured and working
    3. Basic SQL queries can be executed successfully

    Args:
        db (AsyncSession): Database session dependency.

    Raises:
        HTTPException: 
            - 500: If database is not configured correctly
            - 500: If there's an error connecting to the database

    Returns:
        dict: A welcome message if the health check passes.
    """
    try:
        # Execute async query
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
