from __future__ import annotations

from fastapi import FastAPI
from dotenv import load_dotenv

from .routers.query_routes import router as query_router


load_dotenv()  # Load environment variables from .env if present

app = FastAPI(title="Helios Climate Risk API", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Helios Climate Risk API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(query_router)


