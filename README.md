# AnyStockAI: ASX Stock Tracker & Signal Predictor

## Architecture Overview

**Backend & ML Hosting:**
- Python (FastAPI) for API endpoints and ML inference
- Azure Functions (Python) for scheduled ASX data fetching
- Azure Machine Learning for model training/retraining pipelines

**Frontend:**
- React + TypeScript for user interface
- Azure SignalR Service for real-time price/signal updates

**Data Store:**
- Azure SQL Database for time-series price/signal data
- Azure Blob Storage for historical CSV dumps

**Infrastructure:**
- Azure App Service (or Container Instances/AKS) for hosting API/model
- Azure Functions for scheduled jobs
- Azure Machine Learning workspace for retraining
- Azure Key Vault for secrets

## Project Structure
```
AnyStockAI/
├── backend/         # FastAPI app, ML models, Azure Functions
├── frontend/        # React + TypeScript web app
├── infra/           # Infrastructure-as-code, deployment scripts
├── README.md        # This file
```

## Setup Instructions

1. **Backend**
   - Python 3.10+
   - FastAPI, SQLAlchemy, Azure SDKs
   - Deploy to Azure App Service or Container Instance
   - Use Azure Functions for scheduled data fetch
   - Connect to Azure SQL Database & Blob Storage

2. **Frontend**
   - Node.js 18+
   - React + TypeScript
   - Connect to backend API & Azure SignalR
   - Deploy to Azure App Service

3. **Data & ML**
   - Azure SQL Database for time-series data
   - Azure Blob Storage for CSVs
   - Azure ML workspace for retraining

4. **Infrastructure**
   - Use Bicep/ARM/Terraform for resource provisioning
   - Store secrets in Azure Key Vault

## Features
- Track ASX stocks in real-time
- Predict buy/sell signals using ML
- User-specified stock selection
- Historical data visualization
- Automated retraining pipelines
- Real-time notifications

## Getting Started
- Clone repo, set up Azure resources
- Configure environment variables/secrets
- Run backend & frontend locally for development
- Deploy using provided scripts

---
Replace placeholders with your actual Azure resource names and credentials. See each folder for more details and setup steps.
