"""
Complete setup script: Initialize DB, Load Data, Train Model
"""
import sys
from pathlib import Path
import subprocess

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))


def run_setup():
    """Run complete setup: init DB, load data, train model"""
    print("=" * 60)
    print("Cargo Capacity Prediction - Complete Setup")
    print("=" * 60)
    print()
    
    scripts_dir = Path(__file__).parent
    
    # Step 1: Initialize database
    print("Step 1: Initializing database...")
    try:
        result = subprocess.run(
            [sys.executable, str(scripts_dir / "init_db.py")],
            check=False,
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Database initialized")
        else:
            print(f"⚠️  Database initialization: {result.stderr.strip()}")
            print("   (This is OK if tables already exist)")
    except Exception as e:
        print(f"⚠️  Database initialization: {e}")
        print("   (This is OK if tables already exist)")
    print()
    
    # Step 2: Check if data needs to be loaded
    print("Step 2: Checking for training data...")
    print()
    print("To load data from Google Sheets:")
    print("  1. Export the Google Sheet as CSV")
    print("  2. Run: python scripts/load_google_sheets_data.py <CSV_FILE>")
    print("  OR")
    print("  2. Run: python scripts/load_google_sheets_data.py <GOOGLE_SHEETS_URL>")
    print()
    
    data_loaded = input("Have you already loaded the data? (y/n): ").strip().lower()
    
    if data_loaded != 'y':
        data_source = input("Enter CSV file path or Google Sheets URL (or press Enter to skip): ").strip()
        if data_source:
            print(f"\nLoading data from: {data_source}")
            try:
                result = subprocess.run(
                    [sys.executable, str(scripts_dir / "load_google_sheets_data.py"), data_source],
                    check=True,
                    cwd=backend_dir
                )
                print("✅ Data loaded successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error loading data: {e}")
                return False
            except KeyboardInterrupt:
                print("\n❌ Data loading cancelled")
                return False
        else:
            print("⏭️  Skipping data loading")
    else:
        print("✅ Using existing data")
    print()
    
    # Step 3: Train model
    print("Step 3: Training model...")
    try:
        result = subprocess.run(
            [sys.executable, str(scripts_dir / "train_baggage_model.py")],
            check=True,
            cwd=backend_dir
        )
        print()
        print("✅ Setup complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error training model: {e}")
        return False
    except KeyboardInterrupt:
        print("\n❌ Training cancelled")
        return False


if __name__ == "__main__":
    success = run_setup()
    sys.exit(0 if success else 1)
