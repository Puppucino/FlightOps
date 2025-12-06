"""
Fix database: Add missing columns to flights table
Simple script that uses SQLite ALTER TABLE
"""
import sqlite3
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
db_path = backend_dir / "flight_delays.db"

if not db_path.exists():
    print(f"❌ Database not found at: {db_path}", file=sys.stderr)
    print("Run 'python scripts/init_db.py' first to create the database", file=sys.stderr)
    sys.exit(1)

print(f"Updating database schema: {db_path}", flush=True)
print(flush=True)

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(flights)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    print(f"Existing columns: {', '.join(existing_columns[:5])}...", flush=True)

    columns_to_add = [
        ('baggage_weight_kg', 'REAL'),
        ('baggage_volume_m3', 'REAL'),
        ('cargo_volume_m3', 'REAL'),
        ('fuel_weight_kg', 'REAL'),
        ('fuel_price_per_kg', 'REAL'),
        ('cargo_price_per_kg', 'REAL'),
    ]

    added_count = 0
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE flights ADD COLUMN {column_name} {column_type}")
                print(f"  ✓ Added column: {column_name}", flush=True)
                added_count += 1
            except Exception as e:
                print(f"  ⚠️  Error adding {column_name}: {e}", flush=True, file=sys.stderr)
        else:
            print(f"  - Column already exists: {column_name}", flush=True)

    conn.commit()
    conn.close()

    if added_count > 0:
        print(f"\n✅ Successfully added {added_count} column(s) to flights table", flush=True)
    else:
        print("\n✅ All columns already exist", flush=True)
except Exception as e:
    print(f"\n❌ Error: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
