"""
Vercel Serverless Function Entry Point for FastAPI
This file wraps the FastAPI app to work with Vercel's serverless functions
"""
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Change working directory to backend for relative paths (database, models, etc.)
os.chdir(backend_dir)

from mangum import Mangum
from app.main import app

# Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")
