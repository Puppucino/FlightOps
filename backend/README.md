# Flight Delay Prediction API - Backend

FastAPI backend for intelligent flight delay prediction and cargo forecasting system.

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file:
```bash
copy .env.example .env
# Linux/Mac: cp .env.example .env
```

4. Update `.env` with your configuration

5. Run the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes and endpoints
│   ├── core/          # Core configuration
│   ├── models/        # Data models and schemas
│   ├── services/      # Business logic and ML services
│   ├── utils/         # Utility functions
│   └── main.py        # FastAPI application entry point
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

