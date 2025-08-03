from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Authentication.router import router as auth_router

# Create FastAPI application
app = FastAPI(
    title="VibePrep Backend API",
    description="Authentication and Learning Management System",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication router
app.include_router(auth_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    return {"message": "VibePrep Backend API is running!"}


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is working properly"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
