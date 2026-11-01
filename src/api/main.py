from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from config.logging_config import setup_logging
from src.api.routers import (
    overview,
    cancellations,
    revenue,
    channels,
    guests,
    rooms,
    chat
)

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise REST Analytics & AI Intelligence Gateway for Hotel Bookings",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(overview.router)
app.include_router(cancellations.router)
app.include_router(revenue.router)
app.include_router(channels.router)
app.include_router(guests.router)
app.include_router(rooms.router)
app.include_router(chat.router)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "StayWise AI Gateway",
        "version": "1.0.0",
        "database": settings.POSTGRES_DB
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
