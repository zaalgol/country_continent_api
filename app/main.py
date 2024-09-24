from fastapi import FastAPI
from app.routers import country_router, continent_router

# Initialize the FastAPI app
app = FastAPI(title="Country-Continent API", version="1.0.0")

# Include routers from the routers module
app.include_router(country_router)
app.include_router(continent_router)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the Country-Continent API!"}
