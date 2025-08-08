from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging

from routes import email, summarize, reply, auth
from config import APP_NAME, APP_VERSION

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

logger.info(f"🚀 Starting {APP_NAME} v{APP_VERSION}")
logger.info(f"🌍 Environment: {ENVIRONMENT}")
logger.info(f"🔌 Port: {os.getenv('PORT', '8000')}")

# Dynamic CORS origins based on environment
if ENVIRONMENT == "production":
    allowed_origins = [
        "https://intelli-mail-lyart.vercel.app",  # No trailing slash
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ]
else:
    # Development origins
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

logger.info(f"🔗 Allowed Origins: {allowed_origins}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers with error handling
try:
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    logger.info("✅ Auth routes loaded")
except Exception as e:
    logger.error(f"❌ Failed to load auth routes: {e}")

try:
    app.include_router(email.router, prefix="/emails", tags=["Email Management"])
    logger.info("✅ Email routes loaded")
except Exception as e:
    logger.error(f"❌ Failed to load email routes: {e}")

try:
    app.include_router(summarize.router, prefix="/summarize", tags=["AI Summarization"])
    logger.info("✅ Summarize routes loaded")
except Exception as e:
    logger.error(f"❌ Failed to load summarize routes: {e}")

try:
    app.include_router(reply.router, prefix="/reply", tags=["AI Reply Generation"])
    logger.info("✅ Reply routes loaded")
except Exception as e:
    logger.error(f"❌ Failed to load reply routes: {e}")

@app.get("/")
async def root():
    """Simple root endpoint"""
    return {
        "message": "IntelliMail API is running",
        "status": "healthy",
        "environment": ENVIRONMENT,
        "version": APP_VERSION
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        return {
            "status": "healthy",
            "service": APP_NAME,
            "version": APP_VERSION,
            "environment": ENVIRONMENT,
            "cors_origins": allowed_origins,
            "timestamp": "2025-08-07"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
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
