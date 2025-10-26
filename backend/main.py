from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Import routers
from api.routers import (
    router_endpoints, 
    orchestrator_endpoints, 
    specialist_endpoints, 
    communication_endpoints,
    conversation_endpoints
)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("=" * 60)
    print("Starting Morgan Legal Tender - Task Router API")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Primary AI Model: {os.getenv('PRIMARY_AI_MODEL', 'claude-sonnet-4-5-20250929')}")
    print(f"API Docs: http://localhost:{os.getenv('PORT', '8000')}/docs")
    print("=" * 60)
    
    # Initialize database connection pool, Redis, etc. (if needed later)
    # await database.connect()
    
    yield
    
    # Shutdown
    print("\n" + "=" * 60)
    print("👋 Shutting down Morgan Legal Tender API...")
    print("=" * 60)
    # await database.disconnect()


# Initialize FastAPI app
app = FastAPI(
    title="Morgan Legal Tender - Task Router API",
    description="""
    AI-Powered Task Routing System for Legal Case Management
    
    This API routes detected legal tasks to the most appropriate AI specialist agent.
    
    ## Features
    * Intelligent task routing
    * Load balancing across agents
    * Priority-based routing
    * Real-time agent status
    * Routing analytics
    
    ## AI Specialists
    * **Records Wrangler** - Retrieves missing records and bills
    * **Communication Guru** - Drafts client messages
    * **Legal Researcher** - Finds case law and citations
    * **Voice Scheduler** - Coordinates appointments
    * **Evidence Sorter** - Organizes documents
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Morgan Legal Tender Team",
        "email": "dhyan.sur@gmail.com",
    },
    license_info={
        "name": "MIT",
    }
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    router_endpoints.router,
    prefix="/api/router",
    tags=["Task Router"]
)

app.include_router(
    orchestrator_endpoints.router,
    prefix="/api/orchestrator",
    tags=["Orchestrator"]
)

app.include_router(
    specialist_endpoints.router,
    prefix="/api/specialists",
    tags=["AI Specialists"]
)

app.include_router(
    communication_endpoints.router,
    prefix="/api",
    tags=["Communication"]
)

app.include_router(
    conversation_endpoints.router,
    prefix="/api",
    tags=["Gemini Conversations"]
)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Morgan Legal Tender - Task Router API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "route_task": "/api/router/route",
            "agent_status": "/api/router/agents/status",
            "routing_stats": "/api/router/stats"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "task-router",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# API Info endpoint
@app.get("/api/info", tags=["Info"])
async def api_info():
    """
    Get API configuration and information
    """
    return {
        "service": "Morgan Legal Tender - Task Router",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "ai_models": {
            "primary": os.getenv("PRIMARY_AI_MODEL", "claude-sonnet-4-5-20250929"),
            "fallback": os.getenv("FALLBACK_AI_MODEL", "gemini-2.0-flash-exp")
        },
        "features": {
            "load_balancing": True,
            "priority_routing": True,
            "analytics": True,
            "real_time_status": True
        },
        "supported_task_types": [
            "retrieve_records",
            "client_communication",
            "legal_research",
            "schedule_appointment",
            "document_organization",
            "deadline_reminder",
            "follow_up",
            "draft_letter",
            "court_filing"
        ],
        "available_agents": [
            "records_wrangler",
            "communication_guru",
            "legal_researcher",
            "voice_scheduler",
            "evidence_sorter"
        ]
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# 404 handler
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Custom 404 handler
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": f"The requested endpoint '{request.url.path}' does not exist",
            "hint": "Check /docs for available endpoints",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    print(f"\n🚀 Starting server on {host}:{port}")
    print(f"📚 Documentation: http://localhost:{port}/docs\n")
    
    # Disable auto-reload to prevent .venv file watching issues
    # If you need auto-reload, manually restart the server after changes
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Disabled to prevent .venv watching issues
        log_level="info"
    )