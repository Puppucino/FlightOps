# Flight Delay Prediction Dashboard

An intelligent dashboard system for analyzing and predicting flight delays using machine learning. The system combines weather data, flight routes, airport traffic, passenger data, and aircraft information to provide accurate predictions for both passenger flights and cargo operations.

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI (Python)
- **Machine Learning**: scikit-learn, pandas, numpy
- **Database**: SQLAlchemy (SQLite by default, easily configurable)

## Project Structure

```
CursorHackathon/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes and endpoints
│   │   ├── core/        # Core configuration
│   │   ├── models/      # Data models and schemas
│   │   ├── services/    # Business logic and ML services
│   │   ├── utils/       # Utility functions
│   │   └── main.py      # FastAPI application entry point
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Environment variables template
│   └── README.md        # Backend documentation
│
├── frontend/             # React + TypeScript frontend
│   ├── src/
│   │   ├── api/         # API client
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── types/       # TypeScript definitions
│   │   └── utils/       # Utility functions
│   ├── package.json     # Node dependencies
│   └── README.md        # Frontend documentation
│
├── setup.sh             # Setup script (Linux/Mac)
├── setup.bat            # Setup script (Windows)
└── README.md            # This file
```

## Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure environment:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

6. Edit `.env` file with your configuration

7. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## Features (To Be Implemented)

### Flight Delay Prediction
- Weather-based delay analysis
- Route optimization predictions
- Airport traffic impact analysis
- Aircraft-specific delay factors

### Cargo Prediction System
- Cargo volume forecasting
- Aircraft capacity optimization
- Airport cargo traffic analysis

### Passenger Traffic Prediction
- Airport passenger flow forecasting
- Integration with cargo predictions
- Historical pattern analysis

## Development

### Backend Development
- FastAPI with automatic API documentation
- Modular architecture for easy extension
- ML service layer ready for model integration
- CORS configured for frontend communication

### Frontend Development
- React 18 with TypeScript for type safety
- Vite for fast development and building
- Axios for API communication
- Recharts ready for data visualization

## Environment Variables

### Backend (.env)
- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `DATABASE_URL`: Database connection string
- `CORS_ORIGINS`: Allowed CORS origins
- `WEATHER_API_KEY`: Weather API key (if needed)
- `AVIATION_API_KEY`: Aviation API key (if needed)

### Frontend (.env)
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Next Steps

1. Implement data models for flights, weather, airports
2. Create ML models for delay prediction
3. Build API endpoints for predictions
4. Develop dashboard UI components
5. Integrate real-time data sources
6. Add data visualization components

## License

This project is part of a hackathon development.