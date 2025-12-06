# Database Setup Guide

## Overview

This document provides instructions for setting up and managing the database for the Flight Delay Prediction Dashboard.

## Database Stack

- **Development**: SQLite (default, no setup required)
- **Production Recommended**: PostgreSQL 14+

## Quick Start

### 1. Initialize Database (SQLite - Development)

```bash
cd backend
python scripts/init_db.py
```

This will create a SQLite database file at `backend/flight_delays.db` with all tables.

### 2. Using Alembic Migrations

#### Create Initial Migration

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
```

#### Apply Migrations

```bash
alembic upgrade head
```

#### Create New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

#### Rollback Migration

```bash
alembic downgrade -1  # Rollback one migration
alembic downgrade base  # Rollback all migrations
```

## PostgreSQL Setup (Production)

### 1. Install PostgreSQL

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Or use Chocolatey: `choco install postgresql`

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE flight_delays;

# Create user (optional)
CREATE USER flight_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE flight_delays TO flight_user;
\q
```

### 3. Update Configuration

Update `backend/.env`:

```env
DATABASE_URL=postgresql://flight_user:your_password@localhost:5432/flight_delays
```

### 4. Install PostgreSQL Driver

```bash
cd backend
pip install psycopg2-binary
```

### 5. Initialize Database

```bash
python scripts/init_db.py
# Or use Alembic
alembic upgrade head
```

## Database Schema

See [DATABASE_DESIGN.md](../DATABASE_DESIGN.md) for complete schema documentation.

### Core Tables

- `airports` - Airport information
- `airlines` - Airline information
- `aircraft_types` - Aircraft type specifications
- `aircraft` - Individual aircraft records
- `flights` - Scheduled and actual flight information
- `weather_data` - Historical and current weather conditions
- `airport_traffic` - Historical airport traffic data
- `flight_delay_predictions` - ML predictions for delays
- `cargo_predictions` - ML predictions for cargo demand
- `passenger_traffic_predictions` - ML predictions for passenger traffic
- `ml_models` - ML model metadata

## Database Management

### View Database (SQLite)

```bash
# Using SQLite CLI
sqlite3 backend/flight_delays.db

# Example queries
.tables
.schema airports
SELECT * FROM airports LIMIT 5;
```

### View Database (PostgreSQL)

```bash
psql -U flight_user -d flight_delays

# Example queries
\dt  # List tables
\d airports  # Describe airports table
SELECT * FROM airports LIMIT 5;
```

### Drop All Tables (WARNING: Deletes all data!)

```bash
python scripts/drop_db.py
```

## Environment Variables

Configure in `backend/.env`:

```env
# Database
DATABASE_URL=sqlite:///./flight_delays.db  # SQLite (development)
# DATABASE_URL=postgresql://user:pass@localhost:5432/flight_delays  # PostgreSQL (production)

# API
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# External APIs
WEATHER_API_KEY=your_weather_api_key
AVIATION_API_KEY=your_aviation_api_key

# Environment
ENVIRONMENT=development
```

## Backup and Restore

### SQLite Backup

```bash
# Backup
cp backend/flight_delays.db backend/flight_delays_backup.db

# Or use SQLite backup command
sqlite3 backend/flight_delays.db ".backup 'backend/flight_delays_backup.db'"
```

### PostgreSQL Backup

```bash
# Backup
pg_dump -U flight_user -d flight_delays > backup.sql

# Restore
psql -U flight_user -d flight_delays < backup.sql
```

## Troubleshooting

### SQLite: "Database is locked"

- Ensure no other processes are accessing the database
- Check for open database connections
- Restart the application

### PostgreSQL: Connection refused

- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify connection settings in `.env`
- Check firewall settings
- Verify user permissions

### UUID Type Issues

If you encounter UUID type errors with SQLite:
- The current setup uses PostgreSQL UUID types which SQLAlchemy converts automatically
- For pure SQLite compatibility, models use GUID type wrapper
- See `app/core/types.py` for details

### Migration Issues

If migrations fail:
```bash
# Check current migration state
alembic current

# View migration history
alembic history

# Reset migrations (WARNING: Data loss)
alembic downgrade base
alembic upgrade head
```

## Next Steps

1. ✅ Database schema created
2. ✅ Models defined
3. ✅ Alembic configured
4. ⏳ Seed data scripts (to be created)
5. ⏳ API endpoints for data access
6. ⏳ ML model integration
