"""
Train baggage prediction model from database flight data
"""
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pandas as pd
from sqlalchemy import create_engine, inspect
from app.core.config import settings
from app.services.ml_service import MLService


def train_model_from_database():
    """Train baggage prediction model using data from database"""
    print("Loading data from database...")
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    
    # First, check if baggage_weight_kg column exists
    with engine.connect() as conn:
        from sqlalchemy import text, inspect
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('flights')]
        
        if 'baggage_weight_kg' not in columns:
            print("❌ Missing baggage_weight_kg column in flights table!")
            print("\nPlease run the schema update script first:")
            print("  python scripts/fix_database.py")
            print("\nOr recreate the database:")
            print("  1. Delete: flight_delays.db")
            print("  2. Run: python scripts/init_db.py")
            print("  3. Reload your data")
            return False
    
    # Query flight data with baggage information
    query = """
    SELECT 
        f.flight_number,
        f.scheduled_departure as flight_date,
        o.iata_code as origin,
        d.iata_code as destination,
        at.model as aircraft_type,
        f.passenger_count,
        f.baggage_weight_kg,
        f.baggage_volume_m3,
        f.cargo_weight_tonnes,
        f.cargo_volume_m3
    FROM flights f
    JOIN airports o ON f.origin_airport_id = o.id
    JOIN airports d ON f.destination_airport_id = d.id
    JOIN aircraft a ON f.aircraft_id = a.id
    JOIN aircraft_types at ON a.aircraft_type_id = at.id
    WHERE f.baggage_weight_kg IS NOT NULL
      AND f.passenger_count IS NOT NULL
      AND f.passenger_count > 0
    ORDER BY f.scheduled_departure
    """
    
    try:
        df = pd.read_sql_query(query, engine)
        print(f"Loaded {len(df)} flights with baggage data")
        
        if len(df) == 0:
            print("❌ No training data found in database!")
            print("\nPlease load data first:")
            print("  python scripts/load_google_sheets_data.py <CSV_FILE_OR_URL>")
            return False
        
        # Prepare aircraft_type column (add manufacturer prefix if needed)
        if 'aircraft_type' in df.columns:
            def format_aircraft_type(x):
                if pd.isna(x):
                    return "Unknown"
                x_str = str(x).strip()
                if x_str.startswith('737') or x_str.startswith('Boeing'):
                    return f"Boeing {x_str.replace('Boeing ', '')}"
                elif x_str.startswith('A330') or x_str.startswith('Airbus'):
                    return f"Airbus {x_str.replace('Airbus ', '')}"
                return x_str
            
            df['aircraft_type'] = df['aircraft_type'].apply(format_aircraft_type)
        
        # Calculate missing baggage_volume_m3 if needed (1 kg ≈ 0.015 m³)
        if 'baggage_volume_m3' not in df.columns or df['baggage_volume_m3'].isna().any():
            mask = df['baggage_weight_kg'].notna() & (
                df['baggage_volume_m3'].isna() if 'baggage_volume_m3' in df.columns else True
            )
            if mask.any():
                if 'baggage_volume_m3' not in df.columns:
                    df['baggage_volume_m3'] = None
                df.loc[mask, 'baggage_volume_m3'] = df.loc[mask, 'baggage_weight_kg'] * 0.015
        
        # Remove rows with missing critical data
        initial_count = len(df)
        df = df.dropna(subset=['passenger_count', 'baggage_weight_kg', 'flight_date'])
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            print(f"⚠️  Removed {removed_count} rows with missing critical data")
        
        if len(df) == 0:
            print("❌ No valid training data after cleaning!")
            return False
        
        # Train model
        print("\nTraining baggage prediction model...")
        ml_service = MLService()
        
        metrics = ml_service.train_baggage_model(df)
        
        print("\n✅ Model training completed!")
        print("\nTraining Metrics:")
        print(f"  Weight Model - R²: {metrics['weight_model']['r2']:.3f}, MAE: {metrics['weight_model']['mae']:.2f} kg")
        print(f"  Volume Model - R²: {metrics['volume_model']['r2']:.3f}, MAE: {metrics['volume_model']['mae']:.3f} m³")
        print(f"  Training samples: {metrics['training_samples']}")
        print(f"  Test samples: {metrics['test_samples']}")
        print("\n✅ Models saved to backend/models/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error training model: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("Baggage Prediction Model Training")
    print("=" * 60)
    print()
    
    success = train_model_from_database()
    
    if success:
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Test predictions using the API:")
        print("   POST /api/v1/cargo/predict-capacity")
        print("2. View predictions in the frontend:")
        print("   Navigate to /cargo-analytics")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Training failed. Please check the error above.")
        print("=" * 60)
        sys.exit(1)
