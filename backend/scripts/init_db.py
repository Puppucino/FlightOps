"""
Database initialization script
Creates all database tables
"""
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

try:
    from app.core.database import init_db, engine, Base
    from app.models import *  # Import all models
    from app.core.config import settings
    
    print(f"Initializing database: {settings.DATABASE_URL}")
    print("Creating all tables...")
    print()
    
    # List all tables that will be created
    tables = Base.metadata.tables.keys()
    print(f"Tables to create: {', '.join(sorted(tables))}")
    print()
    
    init_db()
    
    print("✓ Database initialized successfully!")
    print(f"✓ All tables created in: {settings.DATABASE_URL}")
    print(f"✓ Created {len(tables)} tables")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure you have:")
    print("1. Activated the virtual environment: venv\\Scripts\\activate.bat")
    print("2. Installed dependencies: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error initializing database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
