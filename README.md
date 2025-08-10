Helios Climate Risk — CrewAI + SQLite (FastAPI + Streamlit)

Simple, fully local project with no external database dependency. Uses SQLite for persistence, FastAPI for a deterministic backend API, and Streamlit as an optional frontend. A single CrewAI agent calls the API via tools.

Project structure
- `app/backend`: FastAPI, routers, queries, ingestion, database helpers, utils
- `app/frontend`: Streamlit UI for real‑time demo
- `app/crew`: Single-agent setup with tools that call the API

Setup (Windows PowerShell)
1) Create venv and install dependencies
   python -m venv .venv
   . .venv/Scripts/Activate.ps1
   pip install -r requirements.txt

2) Ingest data (creates `data.db`, idempotent upsert from 5 endpoints)
   python -m app.backend.ingest

3) Run API (FastAPI)
   uvicorn app.backend.main:app --host 0.0.0.0 --port 8000 --reload

4) Run Streamlit
   streamlit run app/frontend/streamlit_app.py

CrewAI demo (optional)
- python -m app.crew.run_agent

API endpoints (base prefix: `/api/v1/query`)
- POST `/highest-current-risk`
- POST `/compare-country-year-vs-hist`
- POST `/most-similar-year`
- POST `/global-avg-for-month`
- POST `/top-k-lowest-hist-risk`
- POST `/top-k-highest-current-risk`
- POST `/trend-max-risk`
- POST `/trend-max-risk-overall`
- POST `/country-season-change`
- POST `/country-season-change-overall`
- POST `/yield-and-risk-relation`
- POST `/upcoming-spike-regions`
- POST `/eu-risk-comparison`
- POST `/eu-risk-comparison-overall`

Notes
- Ingestion is idempotent (unique keys); re-run anytime to refresh data.
- Streamlit and CrewAI tools call the same API. You can override the base URL via `API_BASE` env var.

Environment variables:
- OPENAI_MODEL_NAME=gpt-4o-mini
- OPENAI_API_KEY=YOUR-API-KEY-HERE
- API_BASE=http://localhost:8000

Run with Docker
1) Build
   docker compose build

2) Ingest (optional)
   docker compose run --rm api python -m app.backend.ingest

3) Start services
   docker compose up

4) Access
- API docs: http://localhost:8000/docs
- Streamlit: http://localhost:8501
