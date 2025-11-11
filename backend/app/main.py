import os
from fastapi import FastAPI
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routes import auth_routes, ingredient_routes, mealplan_routes, whatsapp_routes
from app.services.scheduler import start_scheduler
from app.database import init_indexes
from app.routes import agentic_routes

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS to allow frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://10.10.247.154:3000",
        # GitHub Pages origin (no path)
        "https://viswanth207.github.io",
        # Vercel deployed frontend
        "https://meal-planner-ai-upay.vercel.app",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])  # auth has no internal prefix
app.include_router(ingredient_routes.router)  # router already has "/ingredients" prefix
app.include_router(mealplan_routes.router)    # router already has "/mealplan" prefix
app.include_router(whatsapp_routes.router)    # router already has "/whatsapp" prefix
app.include_router(agentic_routes.router)     # new orchestration endpoints

@app.on_event("startup")
def _startup():
    try:
        # Always skip DB index initialization on Vercel to avoid cold-start failures
        if os.getenv("VERCEL") == "1":
            logger.info("Skipping MongoDB index initialization on Vercel serverless environment")
        else:
            init_indexes()
            logger.info("MongoDB indexes ensured")
    except Exception as e:
        logger.warning(f"Index initialization failed: {e}")
    try:
        # Disable scheduler on Vercel by default or when explicitly requested
        disable = os.getenv("DISABLE_SCHEDULER", "").lower() in ("1", "true", "yes")
        if os.getenv("VERCEL") == "1" or disable:
            logger.info("Scheduler disabled for serverless environment")
        else:
            start_scheduler()
            logger.info("Scheduler started")
    except Exception as e:
        # Avoid crashing app if scheduler fails
        logger.warning(f"Failed to start scheduler: {e}")

@app.get("/health")
def _health():
    return {"status": "ok"}

# Browsers request /favicon.ico automatically; return 204 to avoid noisy errors
@app.get("/favicon.ico")
def _favicon():
    return Response(status_code=204)
