import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from server.app.api.router import api_router
from server.app.ingestion.kafka_adapter import kafka_adapter
from server.app.observability.logger import logger
import asyncio

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the Kafka consumer loop background task
    logger.info("Starting up server...")
    consumer_task = asyncio.create_task(kafka_adapter.consume_loop())
    yield
    # Shutdown
    logger.info("Shutting down server...")
    kafka_adapter.stop()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Multi-Agent LLM Backend",
    description="Scalable Agentic AI System with RAG",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api/v1")

# Mount frontend
app.mount("/web", StaticFiles(directory="webapp"), name="webapp")

@app.get("/")
def serve_frontend():
    return FileResponse("webapp/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
