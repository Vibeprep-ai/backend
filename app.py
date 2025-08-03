from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Authentication.router import router as auth_router
from Schedule.router import router as calendar_router, connect_to_mongo, close_mongo_connection

app = FastAPI(
    title="Calendar API",
    description="A simple calendar scheduling API with slot management using MongoDB",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Connect to MongoDB on startup"""
    connect_to_mongo()

@app.on_event("shutdown")
def shutdown_event():
    """Close MongoDB connection on shutdown"""
    close_mongo_connection()

app.include_router(calendar_router)
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Welcome to Calendar API",
        "version": "1.0.0",
        "database": "MongoDB",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "calendar": "/calendar"
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running with MongoDB"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )