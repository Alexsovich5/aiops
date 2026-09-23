"""
AIOps Platform - Main Application
"""

import uvicorn
import yaml
import logging
from fastapi import FastAPI
from api.routes import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('aiops')

app = FastAPI(title="AIOps Platform", version="1.0.0")
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "aiops-platform"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
