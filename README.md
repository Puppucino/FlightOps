# Cargo Analytics System

An intelligent cargo capacity prediction and flight analytics platform powered by AI and machine learning. The system provides real-time cargo capacity forecasting, flight delay predictions, and AI-powered insights to optimize cargo operations and maximize revenue.

## 🎯 Product Overview

The **Cargo Analytics System** is a comprehensive solution for airlines and cargo operators to:

- **Predict cargo capacity** days before flights using ML models
- **Forecast flight delays** using real-time weather data and historical patterns
- **Optimize cargo mix** with AI-powered recommendations
- **Monitor operations** with proactive alerts and real-time tracking
- **Get AI insights** through natural language queries and conversational assistant

### Key Capabilities

#### 📦 Cargo Capacity Prediction
- ML-powered predictions for available cargo space (weight & volume)
- Multi-day forecasting (0-30 days before flight)
- Aircraft-specific capacity calculations
- Baggage prediction integration
- Overbooking risk assessment

#### ✈️ Flight Analytics
- Real-time flight tracking via OpenSky Network
- Aircraft information enrichment via ADSBDB
- Route statistics and historical analysis
- Airport capacity and traffic insights
- Weather impact analysis

#### 🤖 AI-Powered Features
- **Conversational AI Assistant**: Natural language chat interface
- **Natural Language Queries**: Ask questions like "Show me flights with high overbooking risk"
- **Automated Insights**: AI explains predictions in plain language
- **Intelligent Recommendations**: Optimal cargo mix suggestions
- **Proactive Alerts**: Real-time monitoring of capacity issues
- **Full Database Access**: AI has complete access to all data and services

#### 📊 Predictive Analytics
- Flight delay prediction with weather integration
- Cargo demand forecasting
- Passenger traffic prediction
- Route performance analysis
- Revenue optimization recommendations

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite for fast development
- Tailwind CSS for styling
- Recharts for data visualization

**Backend:**
- FastAPI (Python) with async/await
- SQLAlchemy 2.0 ORM
- scikit-learn for ML models
- DeepSeek API for AI features

**Database:**
- SQLite (development)
- PostgreSQL (production recommended)
- Alembic for migrations

**External APIs:**
- AviationWeather.gov (METAR data - no API key needed)
- ADSBDB.com (aircraft data - no API key needed)
- OpenSky Network (real-time flight tracking - no API key needed)
- DeepSeek (AI agent - API key required)

### Project Structure

```
CursorHackathon/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes (cargo, AI, tracking, etc.)
│   │   ├── core/        # Configuration and database
│   │   ├── models/      # SQLAlchemy models (11 tables)
│   │   ├── services/    # Business logic (ML, AI, tracking)
│   │   ├── infrastructure/
│   │   │   └── external/  # External API clients
│   │   └── main.py      # FastAPI app entry point
│   ├── models/          # Trained ML models (.joblib)
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/            # React + TypeScript frontend
│   ├── src/
│   │   ├── api/         # API client services
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── types/       # TypeScript definitions
│   └── package.json
│
├── DATABASE_DESIGN.md   # Complete database schema
├── DATABASE_SUMMARY.md  # Quick database reference
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL (optional, SQLite works for development)

### Option 1: Automated Setup

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

1. Navigate to backend:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
# Windows
copy .env.example .env
# Linux/Mac
cp .env.example .env
```

5. Edit `.env` file:
```env
# Required: DeepSeek API key for AI features
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Database (SQLite for dev, PostgreSQL for prod)
DATABASE_URL=sqlite:///./flight_delays.db

# Optional: Other API keys (not required - APIs are public)
WEATHER_API_KEY=
AVIATION_API_KEY=
```

6. Initialize database:
```bash
python scripts/init_db.py
```

7. Run server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

#### Frontend Setup

1. Navigate to frontend:
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

Frontend available at http://localhost:3000

## 📖 Features

### Cargo Analytics Dashboard

- **Flight Selection**: Browse and select flights from calendar or list view
- **Capacity Predictions**: View available cargo space predictions for multiple time horizons
- **Risk Assessment**: See overbooking risk levels (high/medium/low)
- **Visual Analytics**: Charts and graphs for capacity trends
- **Real-time Updates**: Live data refresh

### AI Assistant

- **Natural Language Chat**: Ask questions in plain English
- **Context-Aware**: Understands current flight context
- **Query Examples**:
  - "Show me flights with high overbooking risk next week"
  - "What's the cargo capacity for flight MH123?"
  - "Compare cargo capacity across different routes"
  - "What are the statistics for KUL to SIN route?"

### Proactive Alerts

- **Real-time Monitoring**: Automatic checks for upcoming flights
- **Alert Types**:
  - High overbooking risk
  - Low capacity warnings
  - High capacity opportunities
  - Constraint alerts (weight/volume)
- **Severity Levels**: High, medium, low priority

### Flight Tracking

- **Aircraft Information**: Get detailed aircraft data from ADSBDB
- **Real-time Status**: Track flights via OpenSky Network
- **Route Analysis**: Historical route statistics
- **Airport Insights**: Airport capacity and traffic data

### ML Predictions

- **Cargo Capacity**: Predict available space days before flight
- **Flight Delays**: Weather-based delay predictions
- **Cargo Demand**: Forecast future cargo requirements
- **Passenger Traffic**: Predict passenger volumes

## 🗄️ Database

The system uses a comprehensive database schema with 11 core tables:

- **Flights**: Scheduled and actual flight data
- **Aircraft & AircraftTypes**: Aircraft specifications
- **Airports & Airlines**: Airport and airline information
- **WeatherData**: Historical weather conditions
- **AirportTraffic**: Traffic patterns
- **Predictions**: ML prediction results (delays, cargo, traffic)
- **MLModels**: Model metadata and versions

See [DATABASE_DESIGN.md](DATABASE_DESIGN.md) for complete schema details.

### Database Setup

**Initialize (SQLite - Development):**
```bash
cd backend
python scripts/init_db.py
```

**Using Migrations (Recommended):**
```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
# Required
DEEPSEEK_API_KEY=your_key_here
DATABASE_URL=sqlite:///./flight_delays.db

# Optional (APIs are public, no keys needed)
WEATHER_API_KEY=
AVIATION_API_KEY=

# Server
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env):**
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 📡 API Endpoints

### Cargo Analytics
- `GET /api/v1/cargo/analytics/{flight_id}` - Get cargo analytics
- `POST /api/v1/cargo/predict-capacity` - Predict cargo capacity
- `GET /api/v1/cargo/flights` - List available flights

### AI Agent
- `POST /api/v1/ai/chat` - Conversational AI chat
- `POST /api/v1/ai/query` - Natural language queries
- `POST /api/v1/ai/insights` - Generate insights
- `POST /api/v1/ai/optimize-cargo` - Cargo optimization
- `GET /api/v1/ai/alerts` - Get proactive alerts

### Flight Tracking
- `GET /api/v1/tracking/aircraft/{registration}` - Aircraft info
- `GET /api/v1/tracking/routes/{origin}/{destination}` - Route info
- `GET /api/v1/tracking/realtime/{registration}` - Real-time status
- `GET /api/v1/tracking/airport/{airport}/flights` - Airport flights

### Flight Delay Prediction
- `POST /api/v1/flight-delay/predict/{flight_id}` - Predict delays
- `GET /api/v1/flight-delay/test-weather/{airport_code}` - Test weather API

Full API documentation available at http://localhost:8000/api/docs

## 🤖 AI Features

The system includes a comprehensive AI agent powered by DeepSeek that has:

- **Full Database Access**: Can query all 11 tables
- **Service Integration**: Access to all ML and tracking services
- **Natural Language Understanding**: Parses complex queries
- **Context Awareness**: Understands flight context and relationships
- **Intelligent Recommendations**: Suggests optimal cargo mixes
- **Automated Insights**: Explains predictions in plain language

### Example AI Queries

- "How many flights are in the database?"
- "What are the statistics for KUL to SIN route?"
- "Tell me about flight MH123"
- "Show me all flights with high overbooking risk"
- "What's the average delay on route KUL-SIN?"
- "Optimize cargo for weight-constrained flights"

## 🧪 Development

### Backend Development

- FastAPI with automatic API documentation
- Async/await throughout for performance
- Modular service architecture
- ML model integration ready
- External API clients with rate limiting

### Frontend Development

- React 18 with TypeScript
- Vite for fast HMR
- Component-based architecture
- Responsive design with Tailwind CSS
- Real-time data updates

### Testing

```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test
```

## 📚 Documentation

- **[DATABASE_DESIGN.md](DATABASE_DESIGN.md)** - Complete database schema
- **[DATABASE_SUMMARY.md](DATABASE_SUMMARY.md)** - Quick database reference
- **[DATABASE_QUICK_REF.md](DATABASE_QUICK_REF.md)** - Common database commands
- **[backend/README.md](backend/README.md)** - Backend-specific documentation
- **[frontend/README.md](frontend/README.md)** - Frontend-specific documentation

## 🚀 Production Deployment

### Backend

1. Use PostgreSQL instead of SQLite:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/cargo_analytics
```

2. Set production environment:
```env
ENVIRONMENT=production
```

3. Use a production ASGI server:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

1. Build for production:
```bash
cd frontend
npm run build
```

2. Serve static files with nginx or similar

## 📝 License

This project is part of a hackathon development.

## 🤝 Contributing

This is a hackathon project. For questions or issues, please refer to the documentation or API docs.

---

**Built with ❤️ for intelligent cargo operations**
