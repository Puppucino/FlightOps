#!/bin/bash

# Setup script for Flight Delay Prediction Framework
# This script sets up both backend and frontend

echo "Setting up Flight Delay Prediction Framework..."

# Backend setup
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
echo "Backend setup complete!"
cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
echo "Frontend setup complete!"
cd ..

echo "Framework setup complete!"
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "To start the frontend:"
echo "  cd frontend"
echo "  npm run dev"

