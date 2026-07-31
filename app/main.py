"""
app/main.py
FastAPI entrypoint. Creates the app and wires the webhook routes.
Run the dev server with:
    uvicorn app.main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agent import build_agent

from app.config import settings
from app.webhook import router as webhook_router

# Configure logging so you can debug by reading the console (see PRD: Observability).
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    build_agent()      
    yield             

app = FastAPI(title="Fanpage Chatbot Capstone", lifespan=lifespan)


app.include_router(webhook_router)


@app.get("/")
def health_check() -> dict[str, str]:
    """Open http://localhost:8000/ in a browser to confirm the server is up."""
    return {"status": "ok"}


# TODO (Session 2): build ONE shared agent here at startup (via a FastAPI
# startup event) so we don't rebuild the agent on every incoming message.
