from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from routes import email, summarize, reply, auth
from config import CORS_ORIGINS, APP_NAME, APP_VERSION

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    description="AI-Powered Email Assistant with Gmail Integration",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(email.router, prefix="/emails", tags=["Email Management"])
app.include_router(summarize.router, prefix="/summarize", tags=["AI Summarization"])
app.include_router(reply.router, prefix="/reply", tags=["AI Reply Generation"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Welcome to IntelliMail API",
        "version": APP_VERSION,
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "detail": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
