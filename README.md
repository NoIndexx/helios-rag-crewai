# 🌡️ Helios Climate Risk Chatbot — CrewAI + SQLite

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3+-lightblue.svg)](https://sqlite.org)

> 🚀 **Simple, fully local project** with no external database dependency. Uses SQLite for persistence, FastAPI for a deterministic backend API, and Streamlit as an optional frontend. A single CrewAI agent calls the API via tools.

## 🎯 Project Overview

From testing, most Q&A questions were generic and did not specify a commodity.

**To improve answer accuracy**, decide on one of the following behaviors:
- ✅ Require the user to specify a commodity
- ⚡ Default to absolute numbers when no commodity is provided, and use the specified commodity when present (already implemented for Question 1)
- 🧠 Let the model decide based on short‑term and long‑term memory (used in other endpoints)

## 📁 Project Structure

```
app/
├── 🔧 backend/     # FastAPI, routers, queries, ingestion, database helpers, utils
├── 🎨 frontend/    # Streamlit UI for real‑time demo
└── 🤖 crew/        # Single-agent setup with tools that call the API
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12
- Virtual environment or conda

### 1️⃣ Setup Environment (Windows PowerShell)

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
. .venv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Initialize Database

```bash
# Ingest data (creates data.db, idempotent upsert from 5 endpoints)
python -m app.backend.ingest
```

### 3️⃣ Start Services

```bash
# Run FastAPI backend
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000 --reload

# Run Streamlit frontend (in another terminal)
streamlit run app/frontend/streamlit_app.py
```

### 4️⃣ Optional: CrewAI Demo

```bash
python -m app.crew.run_agent
```

## 🔗 API Endpoints

**Base prefix:** `/api/v1/query`

<details>
<summary>📋 View All Endpoints</summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/highest-current-risk` | Get highest current climate risk |
| `POST` | `/compare-country-year-vs-hist` | Compare country year vs historical data |
| `POST` | `/most-similar-year` | Find most similar year |
| `POST` | `/global-avg-for-month` | Get global average for specific month |
| `POST` | `/top-k-lowest-hist-risk` | Get top K lowest historical risks |
| `POST` | `/top-k-highest-current-risk` | Get top K highest current risks |
| `POST` | `/trend-max-risk` | Analyze maximum risk trends |
| `POST` | `/trend-max-risk-overall` | Overall maximum risk trends |
| `POST` | `/country-season-change` | Country seasonal changes |
| `POST` | `/country-season-change-overall` | Overall country seasonal changes |
| `POST` | `/yield-and-risk-relation` | Yield and risk relationship analysis |
| `POST` | `/upcoming-spike-regions` | Predict upcoming spike regions |
| `POST` | `/eu-risk-comparison` | EU risk comparison |
| `POST` | `/eu-risk-comparison-overall` | Overall EU risk comparison |

</details>

## 🐳 Docker Setup

### Build and Run

```bash
# 1. Build the containers
docker compose build

# 2. Ingest data (optional)
docker compose run --rm api python -m app.backend.ingest

# 3. Start all services
docker compose up
```

### Access Points

- 📚 **API Documentation:** http://localhost:8000/docs
- 🎨 **Streamlit App:** http://localhost:8501

## ⚙️ Environment Variables

```bash
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=YOUR-API-KEY-HERE
API_BASE=http://localhost:8000
```

## 📝 Important Notes

- 🔄 **Ingestion is idempotent** (unique keys); re-run anytime to refresh data
- 🔧 **Streamlit chat** uses CrewAI, and the tools call the FastAPI
- 🧪 **API Tests tab** in Streamlit calls the API directly for debugging
- 🌐 **Override base URL** via `API_BASE` environment variable

## 🚧 Next Steps

### 🔮 Planned Improvements

- [ ] **🧠 Model upgrade**: Use Claude 4 for higher-quality answers and more reliable tool calling

- [ ] **🎯 Tool calling policy**:
  - Enforce absolute numbers or require the commodity name
  - Avoid generic questions that obscure intent and may auto-select a commodity

- [ ] **🏗️ Centralized MCP (FastAPI)**: Create a single FastAPI service to host and expose all tools

- [ ] **💾 Memory architecture**: Store short- and long-term memory in a vector database, partitioned by `thread_id`

- [ ] **🔧 Codebase refactor**: Keep only a FastAPI service dedicated to serving CrewAI logic; retire other components

---

<div align="center">

**Built with ❤️ using FastAPI, Streamlit, and CrewAI**

</div>
