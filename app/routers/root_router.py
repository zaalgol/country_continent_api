from fastapi import APIRouter
import logging

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    logging.info("Root endpoint accessed")
    return {"message": "Welcome to the Country-Continent API!"}