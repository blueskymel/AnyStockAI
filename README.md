# AnyStockAI: ASX Stock Tracker & Signal Predictor

## Architecture Overview

**Backend & ML Hosting:**
- Python (FastAPI) for API endpoints and ML inference
- Azure Functions (Python) for scheduled ASX data fetching
- Azure Machine Learning for model training/retraining pipelines

**Frontend:**
- React + TypeScript for user interface
- WebSocket Service for real-time price/signal updates
- Modern responsive layout and smart styling (see below)

**Data Store:**
- Azure SQL Database for time-series price/signal data
- Azure Blob Storage for historical CSV dumps

**Infrastructure:**
- Azure App Service (or Container Instances/AKS) for hosting API/model
- Azure Functions for scheduled jobs
- Azure Machine Learning workspace for retraining
- Azure Key Vault for secrets
- Docker for local and production deployment

## Project Structure
```
AnyStockAI/
├── backend/         # FastAPI app, ML models, Azure Functions
├── frontend/        # React + TypeScript web app
├── infra/           # Infrastructure-as-code, deployment scripts
├── Dockerfile       # Container config (backend & frontend)
├── docker-compose.yml # Multi-service orchestration
├── README.md        # This file
```

## Setup Instructions

### 1. Local Development (Docker)

#### Prerequisites
- Docker Desktop (Windows/Mac/Linux)
- Node.js 18+ (for local frontend dev)
- Python 3.12+ (for local backend dev)

#### Quick Start (Production-ready)
1. Clone the repo:
   ```sh
   git clone <your-repo-url>
   cd AnyStockAI
   ```
2. Build and run with Docker Compose:
   ```sh
   docker-compose up --build
   ```
   - Backend: FastAPI on port 8000
   - Frontend: React (Nginx) on port 3000
3. Access the app at [http://localhost:3000](http://localhost:3000)

#### Local Development (without Docker)
- Backend:
  ```sh
  cd backend
  python -m venv .venv
  .venv\Scripts\activate  # Windows
  pip install -r requirements.txt
  uvicorn main:app --reload
  ```
- Frontend:
  ```sh
  cd frontend
  npm install --legacy-peer-deps
  npm start
  ```

### 2. Modern Frontend Upgrade
See `frontend/package.upgrade.md` for instructions to migrate to Vite + React for faster builds and modern dependency management.

## Features
- Track ASX stocks in real-time
- Predict buy/sell signals using ML
- User-specified stock selection
- Historical data visualization
- Automated retraining pipelines
- Real-time notifications
- Production-ready Docker setup

## Frontend Style & Layout
- Responsive, clean dashboard layout
- Styled tables for history and price data
- Card-based signal display
- Modern color palette and typography
- Mobile-friendly (media queries)
- See `frontend/src/App.css` for details

## Getting Started
- Clone repo, set up Azure resources
- Configure environment variables/secrets
- Run backend & frontend locally or with Docker
- Deploy using provided scripts or containers

---
Replace placeholders with your actual Azure resource names and credentials. See each folder for more details and setup steps.
