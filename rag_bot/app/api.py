from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from . import config
from .rag import create_bot_from_env


app = FastAPI(title="QuantumForge RAG Bot", version="1.0.0")
bot = create_bot_from_env()


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=config.DEFAULT_TOP_K, ge=1, le=10)
    protection: bool = True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(request: AskRequest):
    response = bot.answer(
        request.question,
        top_k=request.top_k,
        protection=request.protection,
    ).to_dict()
    response.pop("prompt", None)
    return response
