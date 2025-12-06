"""
Database drop script
WARNING: This will delete all data!
"""
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import drop_db
from app.models import *  # Import all models
from app.core.config import settings

print(f"WARNING: This will drop all tables in: {settings.DATABASE_URL}")
response = input("Are you sure you want to continue? (yes/no): ")

if response.lower() != "yes":
    print("Cancelled.")
    sys.exit(0)

try:
    drop_db()
    print("✓ All tables dropped successfully!")
except Exception as e:
    print(f"✗ Error dropping database: {e}")
    sys.exit(1)
