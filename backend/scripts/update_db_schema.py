"""
Update database schema to add new baggage and cargo columns
"""
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.core.database import engine, init_db, Base
from app.models import *  # Import all models to register them
from app.core.config import settings


def update_schema():
    """Add missing columns to flights table"""
    print("Updating database schema...")
    print(f"Database: {settings.DATABASE_URL}")
    print()
    
    try:
        with engine.begin() as conn:
            # Check if flights table exists
            if 'sqlite' in settings.DATABASE_URL.lower():
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='flights'"))
                if not result.fetchone():
                    print("  ⚠️  Flights table doesn't exist. Run init_db.py first.")
                    return False
                
                # Get existing columns
                result = conn.execute(text("PRAGMA table_info(flights)"))
                existing_columns = [row[1] for row in result]
            else:
                # PostgreSQL
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'flights'
                    )
                """))
                if not result.fetchone()[0]:
                    print("  ⚠️  Flights table doesn't exist. Run init_db.py first.")
                    return False
                
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'flights'
                """))
                existing_columns = [row[0] for row in result]
            
            # Check if columns exist and add them if they don't
            columns_to_add = [
                ('baggage_weight_kg', 'DECIMAL(10, 2)', 'REAL'),
                ('baggage_volume_m3', 'DECIMAL(10, 2)', 'REAL'),
                ('cargo_volume_m3', 'DECIMAL(10, 2)', 'REAL'),
                ('fuel_weight_kg', 'DECIMAL(10, 2)', 'REAL'),
                ('fuel_price_per_kg', 'DECIMAL(10, 2)', 'REAL'),
                ('cargo_price_per_kg', 'DECIMAL(10, 2)', 'REAL'),
            ]
            
            added_count = 0
            for column_name, pg_type, sqlite_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        col_type = sqlite_type if 'sqlite' in settings.DATABASE_URL.lower() else pg_type
                        conn.execute(text(f"ALTER TABLE flights ADD COLUMN {column_name} {col_type}"))
                        print(f"  ✓ Added column: {column_name}")
                        added_count += 1
                    except Exception as e:
                        print(f"  ⚠️  Error adding {column_name}: {e}")
                else:
                    print(f"  - Column already exists: {column_name}")
            
            if added_count > 0:
                print(f"\n✓ Added {added_count} new column(s)")
            else:
                print("\n✓ All columns already exist")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting schema update...")
    try:
        success = update_schema()
        if success:
            print("\n✅ Schema update completed successfully!")
        else:
            print("\n⚠️  Schema update completed with warnings")
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
