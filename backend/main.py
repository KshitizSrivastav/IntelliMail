from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

from routes import email, summarize, reply, auth
from config import APP_NAME, APP_VERSION

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    description="AI-Powered Email Assistant with Gmail Integration",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Dynamic CORS origins based on environment
if ENVIRONMENT == "production":
    allowed_origins = [
        "https://intellimail.vercel.app",  # Replace with your actual Vercel domain
        "https://*.vercel.app",  # Allow all Vercel preview deployments
        "https://intellimail-frontend.vercel.app",  # Alternative naming
    ]
else:
    # Development origins
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

print(f"🌍 Environment: {ENVIRONMENT}")
print(f"🔗 Allowed Origins: {allowed_origins}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
        "environment": ENVIRONMENT,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "cors_origins": allowed_origins
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if ENVIRONMENT == "development" else "An error occurred",
            "detail": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=ENVIRONMENT == "development",
        log_level="info"
    )
