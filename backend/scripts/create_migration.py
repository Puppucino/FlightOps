"""
Helper script to create Alembic migrations
"""
import sys
import subprocess
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_migration.py <migration_message>")
        print('Example: python create_migration.py "Add new column to flights"')
        sys.exit(1)
    
    message = sys.argv[1]
    
    print(f"Creating migration: {message}")
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        cwd=backend_dir
    )
    
    if result.returncode == 0:
        print("✓ Migration created successfully!")
        print("\nNext steps:")
        print("1. Review the migration file in alembic/versions/")
        print("2. Apply migration: alembic upgrade head")
    else:
        print("✗ Migration creation failed")
        sys.exit(1)
