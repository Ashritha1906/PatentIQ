import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.routes import health, search, novelty, analyze, knowledge, copilot, compare, innovation, reports

# Configure API logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("PatentIQ-API")

app = FastAPI(
    title="PatentIQ API",
    description="Production API Layer for Patent IQ RAG Intelligence Analysis",
    version="1.0.0"
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes under API sub-paths
app.include_router(health.router, prefix="/api", tags=["System Health"])
app.include_router(search.router, prefix="/api", tags=["Retrieval Search"])
app.include_router(novelty.router, prefix="/api", tags=["Novelty Assessment"])
app.include_router(analyze.router, prefix="/api", tags=["Full Intelligence Analysis"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Live Knowledge Expansion"])
app.include_router(copilot.router, prefix="/api", tags=["AI Research Copilot"])
app.include_router(compare.router, prefix="/api", tags=["Patent Comparison & Deep-Dive"])
app.include_router(innovation.router, prefix="/api", tags=["Innovation & Idea Refinement"])
app.include_router(reports.router, prefix="/api", tags=["Research Intelligence Reports"])

# Setup static files directory mapping for frontend client
# Use absolute paths relative to this file to handle uvicorn launched from subdirectories
api_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(api_dir, "..", ".."))

dist_path = os.path.join(project_root, "frontend", "dist")
src_frontend_path = os.path.join(project_root, "frontend")

if os.path.exists(dist_path):
    frontend_path = dist_path
    logger.info(f"FastAPI: Serving compiled React build from: {frontend_path}")
elif os.path.exists(src_frontend_path):
    frontend_path = src_frontend_path
    logger.info(f"FastAPI: Serving source assets from fallback directory: {frontend_path}")
else:
    frontend_path = os.path.join(project_root, "frontend")
    logger.info(f"FastAPI: Fallback path configured: {frontend_path}")

# Serve frontend SPA at root URL
@app.get("/")
def serve_spa():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": f"PatentIQ API is active. Looking for index.html at {index_file}"}

# Mount static folders for client resources
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")