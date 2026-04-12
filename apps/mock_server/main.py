"""
Mock Server for License Plate System
=====================================
Serves static images for the vehicle license plate recognition system.

SNAPSHOT_BASE_URL: http://localhost:8088/static/vnlp_xe_may_sample10/images
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

app = FastAPI(
    title="LPR Mock Image Server",
    description="Serves static images for the license plate recognition system",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "mock_server",
            "version": "1.0.0"
        }
    )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "LPR Mock Image Server",
        "snapshot_base_url": "http://localhost:8088/static/vnlp_xe_may_sample10/images",
        "health_endpoint": "/health",
        "docs": "/docs"
    }


# Mount static files for serving images
# In Docker: /data/processed/vnlp_xe_may_sample10/images
# Local dev: Use DATA_PATH environment variable
DATA_PATH = os.environ.get(
    "DATA_PATH", 
    "/data/processed/vnlp_xe_may_sample10/images"
)

if os.path.exists(DATA_PATH):
    app.mount(
        "/static/vnlp_xe_may_sample10/images",
        StaticFiles(directory=DATA_PATH),
        name="images"
    )
else:
    @app.get("/static/vnlp_xe_may_sample10/images/{path:path}")
    async def fallback_images(path: str):
        """Fallback when image directory is not mounted."""
        return JSONResponse(
            status_code=503,
            content={
                "error": "Image directory not mounted",
                "expected_path": DATA_PATH,
                "requested_file": path
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)
